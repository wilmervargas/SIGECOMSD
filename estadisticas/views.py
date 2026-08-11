
import os
import logging
from io import BytesIO
from datetime import datetime
from openpyxl.drawing.image import Image as OpenpyxlImage
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from xhtml2pdf import pisa

from . import views
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.db import IntegrityError, transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.db.models import Q, F, Sum, Prefetch  # <--- Agrega Prefetch aquí
# Importaciones de modelos y formularios de estadisticas
from salidas.models import SalidaEncabezado, SalidaDetalle
from estadisticas.forms import EstadisticaEncabezadoForm, EstadisticaDetalleFormSet, EstadisticaFilterForm
from django.utils import timezone

logger = logging.getLogger(__name__)
@login_required
def listado_ranking_salidas(request):
    hoy = timezone.now().date()
    primer_dia_mes = hoy.replace(day=1)
    params = request.GET.copy()
    
    # 1. Filtros (Mantenemos tu lógica de Q objects)
    q_objects = Q()
    filtros_activos = any(key not in ['page'] for key in params.keys())
    
    if not params or not filtros_activos:
        filter_form = EstadisticaFilterForm(initial={'fecha_requi_desde': primer_dia_mes, 'fecha_requi_hasta': hoy, 'estado': 'PROCESADA'})
        q_objects = Q(encabezado__fecha_requi__gte=primer_dia_mes, encabezado__fecha_requi__lte=hoy, encabezado__estado='PROCESADA')
    else:
        filter_form = EstadisticaFilterForm(params)
        if filter_form.is_valid():
            cd = filter_form.cleaned_data
            if cd.get('num_requis'): q_objects &= Q(encabezado__num_requis__icontains=cd.get('num_requis'))
            if cd.get('estado'): q_objects &= Q(encabezado__estado=cd.get('estado'))
            #if cd.get('fecha_aprobacion'): q_objects &= Q(encabezado__fecha_aprobacion=cd.get('fecha_aprobacion'))
            if cd.get('fecha_requi_desde'): q_objects &= Q(encabezado__fecha_requi__gte=cd.get('fecha_requi_desde'))
            if cd.get('fecha_requi_hasta'): q_objects &= Q(encabezado__fecha_requi__lte=cd.get('fecha_requi_hasta'))

    # 2. Agrupación por Producto (Ranking)
    # Agrupamos y sumamos cantidad_entregada y subtotal
    ranking = SalidaDetalle.objects.filter(q_objects).values(
        'cod_producto_id', 'cod_producto__cod_producto','cod_producto__descripcion', 'cod_producto__cantidad',
    ).annotate(
        total_qty=Sum('cant_entregada'),
        total_venta=Sum(F('cant_entregada'))
    ).order_by('-total_qty') # Ordenar de mayor a menor venta

    # 3. Detalles para el desglose lateral
    detalles_raw = SalidaDetalle.objects.filter(q_objects).select_related('encabezado')
    
    # Calculamos los totales generales de todo el queryset filtrado
    totales_general = ranking.aggregate(
        t_cant=Sum('total_qty'),
        t_monto=Sum('total_venta')
    )

    context = {
        'titulo': 'Estadísticas - Ranking de Insumos',
        'ranking': ranking,
        'detalles_raw': detalles_raw,
        'filter_form': filter_form,
        'totales_general': totales_general,  # <--- ESTA ES LA CLAVE
        'full_query_string': params.urlencode(),
    }
    return render(request, 'estadisticas/listado.html', context)


@login_required
def reporte_ranking_salidas_pdf(request):
    hoy = timezone.now().date()
    primer_dia_mes = hoy.replace(day=1)
    params = request.GET.copy()
    
    # 1. DEFINICIÓN DE FILTROS (Misma lógica exacta que la vista de pantalla)
    q_objects = Q()
    # Verificamos si hay filtros activos reales
    filtros_activos = any(key not in ['page', 'order_by'] for key in params.keys())
    
    if not params or not filtros_activos:
        # Filtros por defecto si no hay parámetros
        q_objects = Q(
            encabezado__fecha_requi__gte=primer_dia_mes,
            encabezado__fecha_requi__lte=hoy,
            #encabezado__fecha_aprobacion=hoy,
            encabezado__estado='PROCESADA'
        )
    else:
        # Usamos el formulario para validar y construir q_objects
        filter_form = EstadisticaFilterForm(params)
        if filter_form.is_valid():
            cd = filter_form.cleaned_data
            if cd.get('search_query'):
                q_objects &= (Q(encabezado__num_requis__icontains=cd.get('search_query')) | 
                              Q(encabezado__num_ctto_fact__icontains=cd.get('search_query')))
            if cd.get('num_requis'): q_objects &= Q(encabezado__num_requis__icontains=cd.get('num_requis'))
            if cd.get('estado'): q_objects &= Q(encabezado__estado=cd.get('estado'))
            #if cd.get('fecha_aprobacion'): q_objects &= Q(encabezado__fecha_aprobacion=cd.get('fecha_aprobacion'))
            if cd.get('fecha_requi_desde'): q_objects &= Q(encabezado__fecha_requi__gte=cd.get('fecha_requi_desde'))
            if cd.get('fecha_requi_hasta'): q_objects &= Q(encabezado__fecha_requi__lte=cd.get('fecha_requi_hasta'))

    # 2. LÓGICA DE AGRUPACIÓN POR PRODUCTO (RANKING)
    # Obtenemos los totales por cada producto individual
    ranking_queryset = SalidaDetalle.objects.filter(q_objects).values(
        'cod_producto_id', 'cod_producto__cod_producto','cod_producto__descripcion', 'cod_producto__cantidad',
    ).annotate(
        total_qty=Sum('cant_entregada'),
        # Calculamos monto total: Suma de (cantidad * precio) de cada detalle
        total_venta=Sum(F('cant_entregada'))
    ).order_by('-total_qty') # Ordenar de mayor a menor venta (Ranking)

    # 3. OBTENER DETALLES ASOCIADOS PARA EL DESGLOSE
    # Traemos todos los detalles para armar el diccionario de desglose
    todos_los_detalles = SalidaDetalle.objects.filter(q_objects).select_related('encabezado', 'cod_producto')
    
    # Organizamos los detalles en un diccionario para fácil acceso en el template
    # Estructura: { id_producto: [lista_de_detalles] }
    detalles_por_producto = {}
    for det in todos_los_detalles:
        pid = det.cod_producto_id
        if pid not in detalles_por_producto:
            detalles_por_producto[pid] = []
        detalles_por_producto[pid].append(det)

    # 4. TOTALES GLOBALES PARA EL FOOTER DEL REPORTE
    totales_general = ranking_queryset.aggregate(
        t_cant=Sum('total_qty'),
        t_monto=Sum('total_venta')
    )

    # 5. LOGO (Mantenemos tu lógica existente)
    try:
        # Ajusta esta ruta según donde tengas tu logo para PDF
        logo_url = request.build_absolute_uri('/static/img/logo2.png') 
    except Exception:
        logo_url = "" 

    # 6. CONTEXTO PARA EL TEMPLATE PDF
    context = {
        'titulo_reporte': 'RANKING INSUMOS PROCESADOS / POR PERIODOS',
        'ranking': ranking_queryset,
        'detalles_raw': todos_los_detalles, # <--- AÑADE ESTA LÍNEA
        'detalles_dict': detalles_por_producto,
        'totales_general': totales_general,
        'logo_path': logo_url,
        'fecha_emision': datetime.now(),
    }
    
    # 7. GENERACIÓN DEL PDF (xhtml2pdf)
    template = get_template('reportes/reporte_ranking_salidas_pdf.html') # Asegúrate de usar esta ruta
    html = template.render(context)
    result = BytesIO()
    
    pisa_status = pisa.CreatePDF(
        html, 
        dest=result, 
        encoding='utf-8', 
        link_callback=lambda uri, rel: uri # Importante para imágenes locales
    )
    
    if pisa_status.err: 
        return HttpResponse('Error al generar el reporte PDF', status=500)

    # 8. RESPUESTA HTTP
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    filename = f"Ranking_Productos_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

