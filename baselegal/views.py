
import os
import logging
from datetime import datetime
from io import BytesIO
from xhtml2pdf import pisa

from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage
from django.contrib.staticfiles import finders
from django.http import Http404, HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

# SEGURIDAD E HISTÓRICO DE LOS REGISTROS (AUDITORÍA)
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION

# IMPORTACIÓN DE MODELOS Y FORMULARIOS PROPIOS DEL MÓDULO (CORREGIDOS)
from .models import BaselegalDB, BaselegalHistoricoDB
from .forms import BaselegalForm, BaselegalHistoricoForm, BaselegalFilterForm, BaselegalHistoricoFormSet

logger = logging.getLogger(__name__)

# =================================================================
# VISTA PRINCIPAL DE BASE LEGAL CON FILTROS Y ORDENACIÓN
# =================================================================
@login_required
def listado_baselegal(request):
    filter_form = BaselegalFilterForm(request.GET)
    # Optimizamos la consulta con select_related y prefetch_related para el histórico
    queryset_baselegal = BaselegalDB.objects.all().prefetch_related('historicos')  # Prefetch para el histórico relacionado

    # =========================================================
    # 📌 PERSISTENCIA TOTAL: Captura filtros, orden Y página
    # =========================================================
    full_query_params = request.GET.copy()
    query_string_with_page = full_query_params.urlencode()
    
    paginator_params = full_query_params.copy()
    if 'page' in paginator_params:
        del paginator_params['page']
    query_string_for_paginator = paginator_params.urlencode()

    clean_params = paginator_params.copy()
    if 'order_by' in clean_params:
        del clean_params['order_by']
    clean_query_string = clean_params.urlencode()
    # =========================================================

    # Procesamiento de Filtros del Formulario
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        search_query = data.get('search_query')
        if search_query:
            # Como cod_actual y titulo_actual están en el Histórico, filtramos a través de la relación inversa
            queryset_baselegal = queryset_baselegal.filter(
                Q(historicos__cod_actual__icontains=search_query) | 
                Q(historicos__titulo_actual__icontains=search_query)
            ).distinct()

    # Ordenación por ID o por el campo seleccionado
    order_by_principal = request.GET.get('order_by', 'id') 
    campos_ordenar = [order_by_principal]
    
    lista_baselegal = queryset_baselegal.order_by(*campos_ordenar) 

    # Paginación
    page_number = request.GET.get('page', 1)
    paginator = Paginator(lista_baselegal, 50)  # Cambiado a 50 registros por página
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    except Exception:
        raise Http404('*** Página no encontrada ***')

    datos = {
        'titulo': 'Tabla Maestro de Base Legal',
        'subpagina': 'subpage',
        'entity': page_obj, 
        'paginator': paginator,
        'order_by': order_by_principal,
        'filter_form': filter_form,
        
        # Variables de persistencia de URLs
        'query_string': query_string_for_paginator,  
        'full_query_string': query_string_with_page, 
        'clean_query_string': clean_query_string,
        'retorno_url': query_string_with_page,    
    }
    return render(request, 'baselegal/listado.html', datos)


# =================================================================
# VISTA: CREAR Baselegal (CORREGIDA CON ADAPTACIÓN DE SUBFORMULARIO)
# =================================================================
@login_required
def crear_baselegal(request):
    query_string = request.GET.get('query_string', '')
    
    # 1.- FORZAR QUE SOLO APAREZCA UN ÚNICO REGISTRO EN BLANCO EN EL DETALLE
    BaselegalHistoricoFormSet.extra = 1
    
    if request.method == 'POST':
        # SE AGREGA request.FILES PARA CAPTURAR LOS ARCHIVOS SUBIDOS
        formulario = BaselegalForm(request.POST, request.FILES)
        formset = BaselegalHistoricoFormSet(request.POST, request.FILES, instance=None)
        
        if formulario.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Guardar el encabezado primero para obtener el ID principal
                    baselegal_guardado = formulario.save()
                    
                    # 2.- CONTROL DE SUBFORMULARIO: FILTRADO SEGURO DE REGISTROS EN BLANCO
                    formset.instance = baselegal_guardado
                    historicos = formset.save(commit=False)
                    for historico in historicos:
                        # Si es una fila nueva y viene vacía en los campos clave, se ignora y no se guarda
                        if not historico.pk and not historico.cod_baselegal and not historico.titulo:
                            continue
                        historico.save()
                    
                    # Procesar eliminaciones explícitas (en caso de que el usuario borre filas en el cliente)
                    for obj in formset.deleted_objects:
                        obj.delete()
                        
                    formset.save_m2m()
                    
                    # Registro de auditoría
                    LogEntry.objects.create(
                        user_id=request.user.id,
                        content_type_id=ContentType.objects.get_for_model(BaselegalDB).id,
                        object_id=baselegal_guardado.id,
                        object_repr=str(baselegal_guardado),
                        action_flag=ADDITION,
                        change_message="Creó un nuevo baselegal en el sistema."
                    )
                    
                    messages.success(request, "Base Legal registrada con éxito!")
                    if request.POST.get('query_string'):
                        return redirect(reverse('listado_baselegal') + '?' + request.POST.get('query_string'))
                    return redirect('listado_baselegal')
                    
            except IntegrityError as e:
                logger.error(f"Error de integridad al crear baselegal: {str(e)}")
                messages.error(request, "Error: El ID o código ingresado ya se encuentra en uso.")
    else:
        formulario = BaselegalForm()
        formset = BaselegalHistoricoFormSet(instance=None)
        
    context = {
        'formulario': formulario,
        'formset': formset,
        'titulo': "SIGEDOC - Registrar Nuevo Baselegal",
        'query_string': query_string,
    }
    return render(request, 'baselegal/crear.html', context)


# =================================================================
# VISTA: EDITAR Baselegal (CORREGIDA)
# =================================================================
@login_required
def editar_baselegal(request, id):
    baselegal = get_object_or_404(BaselegalDB, id=id)
    query_string = request.GET.get('query_string', '')
    
    # 1.- FORZAR QUE SOLO APAREZCA UN ÚNICO REGISTRO EN BLANCO
    BaselegalHistoricoFormSet.extra = 1
    
    if request.method == 'POST':
        # SE AGREGA request.FILES PARA PROCESAR NUEVOS ARCHIVOS O DESVINCULACIONES
        formulario = BaselegalForm(request.POST, request.FILES, instance=baselegal)
        formset = BaselegalHistoricoFormSet(request.POST, request.FILES, instance=baselegal)
        
        if formulario.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    original = BaselegalDB.objects.get(id=id)
                    
                    # Solo se genera histórico si cambió el código del baselegal
                    if original.cod_baselegal != formulario.cleaned_data.get('cod_baselegal'):
                        BaselegalHistoricoDB.objects.create(
                            baselegal=original,
                            cod_baselegal=original.cod_baselegal,
                            titulo=original.titulo,
                            fecha_publicacion=original.fecha_publicacion,
                            fecha_aprobacion=original.fecha_aprobacion,
                            nro_gaceta=original.nro_gaceta,
                            tipo=original.tipo,
                            organo_publica=original.organo_publica,
                            distribucion_digital=original.distribucion_digital,
                            distribucion_fisica=original.distribucion_fisica,
                            observaciones=original.observaciones,
                            archivo_pdf=original.archivo_pdf  # Mantiene el archivo original en el histórico
                        )

                    baselegal_actualizado = formulario.save()
                    
                    # 2.- CONTROL DE SUBFORMULARIO: FILTRADO SEGURO DE REGISTROS EN BLANCO
                    formset.instance = baselegal_actualizado
                    historicos = formset.save(commit=False)
                    for historico in historicos:
                        # Si es un registro nuevo y no se rellenaron los campos clave, se ignora automáticamente
                        if not historico.pk and not historico.cod_baselegal and not historico.titulo:
                            continue
                        historico.save()
                    
                    # Procesar eliminaciones explícitas de registros existentes
                    for obj in formset.deleted_objects:
                        obj.delete()
                        
                    formset.save_m2m()
                    
                    LogEntry.objects.create(
                        user_id=request.user.id,
                        content_type_id=ContentType.objects.get_for_model(BaselegalDB).id,
                        object_id=baselegal_actualizado.id,
                        object_repr=str(baselegal_actualizado),
                        action_flag=CHANGE,
                        change_message=f"Modificó datos principales. Se generó histórico automático: {original.cod_baselegal} -> {formulario.cleaned_data.get('cod_baselegal')}"
                    )
                    
                    messages.success(request, "¡Baselegal e Historial actualizados correctamente!")
                    if request.POST.get('query_string'):
                        return redirect(reverse('listado_baselegal') + '?' + request.POST.get('query_string'))
                    return redirect('listado_baselegal')
                    
            except IntegrityError as e:
                logger.error(f"Error de integridad al editar baselegal {id}: {str(e)}")
                messages.error(request, "Error de consistencia en la base de datos al guardar los cambios.")
    else:
        formulario = BaselegalForm(instance=baselegal)
        formset = BaselegalHistoricoFormSet(instance=baselegal)
        
    context = {
        'formulario': formulario,
        'formset': formset,
        'titulo': "SIGEDOC - Editar Baselegal",
        'query_string': query_string,
    }
    return render(request, 'baselegal/editar.html', context)

#------------------------------------------
@login_required
def borrar_baselegal(request, id):
    baselegal = get_object_or_404(BaselegalDB, id=id) 
    identificador = f"Num. Base Legal {baselegal.cod_baselegal}"
    query_string = request.POST.get('query_string', request.GET.urlencode())

    try:
        baselegal.delete() # Al borrar el baselegal, se borran en cascada sus históricos por el on_delete=models.CASCADE
        
        LogEntry.objects.create(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(BaselegalDB).id,
            object_id=id, 
            object_repr=f"{identificador} (Borrado)",
            action_flag=DELETION,
            change_message=f'Baselegal {identificador} y su historial eliminados.'
        )
        messages.success(request, f'{identificador} fue eliminado exitosamente', extra_tags='procesado ✅')
        
    except ProtectedError as e:
        logger.error(f"Intento fallido de borrar Baselegal ID {id}: {e}")       
        messages.error(request, "ERROR: No se puede eliminar este baselegal porque está referenciado en otra sección del sistema.", extra_tags='error ❌')
        
    base_url = reverse('listado_baselegal') 
    if query_string:
        return redirect(f'{base_url}?{query_string}')
    return redirect('listado_baselegal')


# ---------------------------------------------------------------------------------
# REPORTE PDF
# ---------------------------------------------------------------------------------
@login_required
def reporte_baselegal_pdf(request):
    search_query = request.GET.get('search_query')
    order_by = request.GET.get('order_by', 'id')

    queryset = BaselegalDB.objects.all().prefetch_related('historicos')
    if search_query:
        queryset = queryset.filter(
            Q(historicos__cod_actual__icontains=search_query) | 
            Q(historicos__titulo_actual__icontains=search_query)
        ).distinct()

    baselegal = queryset.order_by(order_by)

    def link_callback(uri, rel):
        if uri.startswith(settings.STATIC_URL):
            path = uri.replace(settings.STATIC_URL, "")
            result = finders.find(path)
            if result:
                return result
        return uri

    context = {
        'baselegal': baselegal,
        'titulo_reporte': 'Reporte de Baselegal',
        'logo_path': f"{settings.STATIC_URL}img/membrete.png",
        'fecha_emision': datetime.now(),
    }
    
    template = get_template('reportes/reporte_baselegal_pdf.html')
    html = template.render(context)
    result = BytesIO()
    
    pisa_status = pisa.CreatePDF(html, dest=result, encoding='utf-8', link_callback=link_callback)
    if pisa_status.err: 
        return HttpResponse('Error al generar el PDF', status=500)
        
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Reporte_Baselegal.pdf"'
    return response
