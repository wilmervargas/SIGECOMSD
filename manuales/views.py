
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
from .models import ManualesDB, ManualesHistoricoDB
from .forms import ManualForm, ManualesHistoricoForm, ManualFilterForm, ManualesHistoricoFormSet
from dependencias.models import DependenciasBD

logger = logging.getLogger(__name__)

# =================================================================
# VISTA PRINCIPAL DE MANUALES CON FILTROS Y ORDENACIÓN
# =================================================================
@login_required
def listado_manuales(request):
    filter_form = ManualFilterForm(request.GET)
    # Optimizamos la consulta con select_related y prefetch_related para el histórico
    queryset_manuales = ManualesDB.objects.all().select_related('cod_dependencia').prefetch_related('historicos')

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
            queryset_manuales = queryset_manuales.filter(
                Q(historicos__cod_actual__icontains=search_query) | 
                Q(historicos__titulo_actual__icontains=search_query)
            ).distinct()

    # Ordenación por ID o por el campo seleccionado
    order_by_principal = request.GET.get('order_by', 'id') 
    campos_ordenar = [order_by_principal]
    
    lista_manuales = queryset_manuales.order_by(*campos_ordenar) 

    # Paginación
    page_number = request.GET.get('page', 1)
    paginator = Paginator(lista_manuales, 50)  # Cambiado a 50 registros por página
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    except Exception:
        raise Http404('*** Página no encontrada ***')

    datos = {
        'titulo': 'Tabla Maestro de Manuales',
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
    return render(request, 'manuales/listado.html', datos)


# =================================================================
# VISTA: CREAR MANUAL (CORREGIDA CON ADAPTACIÓN DE SUBFORMULARIO)
# =================================================================
@login_required
def crear_manuales(request):
    query_string = request.GET.get('query_string', '')
    
    # 1.- FORZAR QUE SOLO APAREZCA UN ÚNICO REGISTRO EN BLANCO EN EL DETALLE
    ManualesHistoricoFormSet.extra = 1
    
    if request.method == 'POST':
        # SE AGREGA request.FILES PARA CAPTURAR LOS ARCHIVOS SUBIDOS
        formulario = ManualForm(request.POST, request.FILES)
        formset = ManualesHistoricoFormSet(request.POST, request.FILES, instance=None)
        
        if formulario.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Guardar el encabezado primero para obtener el ID principal
                    manual_guardado = formulario.save()
                    
                    # 2.- CONTROL DE SUBFORMULARIO: FILTRADO SEGURO DE REGISTROS EN BLANCO
                    formset.instance = manual_guardado
                    historicos = formset.save(commit=False)
                    for historico in historicos:
                        # Si es una fila nueva y viene vacía en los campos clave, se ignora y no se guarda
                        if not historico.pk and not historico.cod_manual and not historico.titulo:
                            continue
                        historico.save()
                    
                    # Procesar eliminaciones explícitas (en caso de que el usuario borre filas en el cliente)
                    for obj in formset.deleted_objects:
                        obj.delete()
                        
                    formset.save_m2m()
                    
                    # Registro de auditoría
                    LogEntry.objects.create(
                        user_id=request.user.id,
                        content_type_id=ContentType.objects.get_for_model(ManualesDB).id,
                        object_id=manual_guardado.id,
                        object_repr=str(manual_guardado),
                        action_flag=ADDITION,
                        change_message="Creó un nuevo manual en el sistema."
                    )
                    
                    messages.success(request, "¡Manual registrado con éxito!")
                    if request.POST.get('query_string'):
                        return redirect(reverse('listado_manuales') + '?' + request.POST.get('query_string'))
                    return redirect('listado_manuales')
                    
            except IntegrityError as e:
                logger.error(f"Error de integridad al crear manual: {str(e)}")
                messages.error(request, "Error: El ID o código ingresado ya se encuentra en uso.")
    else:
        formulario = ManualForm()
        formset = ManualesHistoricoFormSet(instance=None)
        
    context = {
        'formulario': formulario,
        'formset': formset,
        'titulo': "SIGEDOC - Registrar Nuevo Manual",
        'query_string': query_string,
    }
    return render(request, 'manuales/crear.html', context)


# =================================================================
# VISTA: EDITAR MANUAL (CORREGIDA)
# =================================================================
@login_required
def editar_manuales(request, id):
    manual = get_object_or_404(ManualesDB, id=id)
    query_string = request.GET.get('query_string', '')
    
    # 1.- FORZAR QUE SOLO APAREZCA UN ÚNICO REGISTRO EN BLANCO
    ManualesHistoricoFormSet.extra = 1
    
    if request.method == 'POST':
        # SE AGREGA request.FILES PARA PROCESAR NUEVOS ARCHIVOS O DESVINCULACIONES
        formulario = ManualForm(request.POST, request.FILES, instance=manual)
        formset = ManualesHistoricoFormSet(request.POST, request.FILES, instance=manual)
        
        if formulario.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    original = ManualesDB.objects.get(id=id)
                    
                    # Solo se genera histórico si cambió el código del manual
                    if original.cod_manual != formulario.cleaned_data.get('cod_manual'):
                        ManualesHistoricoDB.objects.create(
                            manual=original,
                            cod_manual=original.cod_manual,
                            titulo=original.titulo,
                            fecha_elaboracion=original.fecha_elaboracion,
                            fecha_revision=original.fecha_revision,
                            fecha_aprobacion=original.fecha_aprobacion,
                            version=original.version,
                            distribucion_digital=original.distribucion_digital,
                            distribucion_fisica=original.distribucion_fisica,
                            observaciones=original.observaciones,
                            archivo_pdf=original.archivo_pdf  # Mantiene el archivo original en el histórico
                        )

                    manual_actualizado = formulario.save()
                    
                    # 2.- CONTROL DE SUBFORMULARIO: FILTRADO SEGURO DE REGISTROS EN BLANCO
                    formset.instance = manual_actualizado
                    historicos = formset.save(commit=False)
                    for historico in historicos:
                        # Si es un registro nuevo y no se rellenaron los campos clave, se ignora automáticamente
                        if not historico.pk and not historico.cod_manual and not historico.titulo:
                            continue
                        historico.save()
                    
                    # Procesar eliminaciones explícitas de registros existentes
                    for obj in formset.deleted_objects:
                        obj.delete()
                        
                    formset.save_m2m()
                    
                    LogEntry.objects.create(
                        user_id=request.user.id,
                        content_type_id=ContentType.objects.get_for_model(ManualesDB).id,
                        object_id=manual_actualizado.id,
                        object_repr=str(manual_actualizado),
                        action_flag=CHANGE,
                        change_message=f"Modificó datos principales. Se generó histórico automático: {original.cod_manual} -> {formulario.cleaned_data.get('cod_manual')}"
                    )
                    
                    messages.success(request, "¡Manual e Historial actualizados correctamente!")
                    if request.POST.get('query_string'):
                        return redirect(reverse('listado_manuales') + '?' + request.POST.get('query_string'))
                    return redirect('listado_manuales')
                    
            except IntegrityError as e:
                logger.error(f"Error de integridad al editar manual {id}: {str(e)}")
                messages.error(request, "Error de consistencia en la base de datos al guardar los cambios.")
    else:
        formulario = ManualForm(instance=manual)
        formset = ManualesHistoricoFormSet(instance=manual)
        
    context = {
        'formulario': formulario,
        'formset': formset,
        'titulo': "SIGEDOC - Editar Manual",
        'query_string': query_string,
    }
    return render(request, 'manuales/editar.html', context)

#------------------------------------------
@login_required
def borrar_manuales(request, id):
    manual = get_object_or_404(ManualesDB, id=id) 
    identificador = f"Cod. Manual {manual.cod_manual}"
    query_string = request.POST.get('query_string', request.GET.urlencode())

    try:
        manual.delete() # Al borrar el manual, se borran en cascada sus históricos por el on_delete=models.CASCADE
        
        LogEntry.objects.create(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(ManualesDB).id,
            object_id=id, 
            object_repr=f"{identificador} (Borrado)",
            action_flag=DELETION,
            change_message=f'Manual {identificador} y su historial eliminados.'
        )
        messages.success(request, f'{identificador} fue eliminado exitosamente', extra_tags='procesado ✅')
        
    except ProtectedError as e:
        logger.error(f"Intento fallido de borrar Manual ID {id}: {e}")       
        messages.error(request, "ERROR: No se puede eliminar este manual porque está referenciado en otra sección del sistema.", extra_tags='error ❌')
        
    base_url = reverse('listado_manuales') 
    if query_string:
        return redirect(f'{base_url}?{query_string}')
    return redirect('listado_manuales')


# ---------------------------------------------------------------------------------
# REPORTE PDF
# ---------------------------------------------------------------------------------
@login_required
def reporte_manuales_pdf(request):
    search_query = request.GET.get('search_query')
    order_by = request.GET.get('order_by', 'id')

    queryset = ManualesDB.objects.all().prefetch_related('historicos')
    if search_query:
        queryset = queryset.filter(
            Q(historicos__cod_actual__icontains=search_query) | 
            Q(historicos__titulo_actual__icontains=search_query)
        ).distinct()

    manuales = queryset.order_by(order_by)

    def link_callback(uri, rel):
        if uri.startswith(settings.STATIC_URL):
            path = uri.replace(settings.STATIC_URL, "")
            result = finders.find(path)
            if result:
                return result
        return uri

    context = {
        'manuales': manuales,
        'titulo_reporte': 'Reporte de Manuales',
        'logo_path': f"{settings.STATIC_URL}img/logo2.png",
        'fecha_emision': datetime.now(),
    }
    
    template = get_template('reportes/reporte_manuales_pdf.html')
    html = template.render(context)
    result = BytesIO()
    
    pisa_status = pisa.CreatePDF(html, dest=result, encoding='utf-8', link_callback=link_callback)
    if pisa_status.err: 
        return HttpResponse('Error al generar el PDF', status=500)
        
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Reporte_Manuales.pdf"'
    return response

