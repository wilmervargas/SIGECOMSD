
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
from .models import ProtocolosDB, ProtocolosHistoricoDB
from .forms import ProtocoloForm, ProtocolosHistoricoForm, ProtocoloFilterForm, ProtocolosHistoricoFormSet
from dependencias.models import DependenciasBD

logger = logging.getLogger(__name__)

# =================================================================
# VISTA PRINCIPAL DE PROTOCOLOS CON FILTROS Y ORDENACIÓN
# =================================================================
@login_required
def listado_protocolos(request):
    filter_form = ProtocoloFilterForm(request.GET)
    # Optimizamos la consulta con select_related y prefetch_related para el histórico
    queryset_protocolos = ProtocolosDB.objects.all().select_related('cod_dependencia').prefetch_related('historicos')

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
            queryset_protocolos = queryset_protocolos.filter(
                Q(historicos__cod_actual__icontains=search_query) | 
                Q(historicos__titulo_actual__icontains=search_query)
            ).distinct()

    # Ordenación por ID o por el campo seleccionado
    order_by_principal = request.GET.get('order_by', 'id') 
    campos_ordenar = [order_by_principal]
    
    lista_protocolos = queryset_protocolos.order_by(*campos_ordenar) 

    # Paginación
    page_number = request.GET.get('page', 1)
    paginator = Paginator(lista_protocolos, 50)  # Cambiado a 50 registros por página
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    except Exception:
        raise Http404('*** Página no encontrada ***')

    datos = {
        'titulo': 'Tabla Maestro de Protocolos',
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
    return render(request, 'protocolos/listado.html', datos)


# =================================================================
# VISTA: CREAR PROTOCOLO (CORREGIDA CON ADAPTACIÓN DE SUBFORMULARIO)
# =================================================================
@login_required
def crear_protocolos(request):
    query_string = request.GET.get('query_string', '')
    
    # 1.- FORZAR QUE SOLO APAREZCA UN ÚNICO REGISTRO EN BLANCO EN EL DETALLE
    ProtocolosHistoricoFormSet.extra = 1
    
    if request.method == 'POST':
        # SE AGREGA request.FILES PARA CAPTURAR LOS ARCHIVOS SUBIDOS
        formulario = ProtocoloForm(request.POST, request.FILES)
        formset = ProtocolosHistoricoFormSet(request.POST, request.FILES, instance=None)
        
        if formulario.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Guardar el encabezado primero para obtener el ID principal
                    protocolo_guardado = formulario.save()
                    
                    # 2.- CONTROL DE SUBFORMULARIO: FILTRADO SEGURO DE REGISTROS EN BLANCO
                    formset.instance = protocolo_guardado
                    historicos = formset.save(commit=False)
                    for historico in historicos:
                        # Si es una fila nueva y viene vacía en los campos clave, se ignora y no se guarda
                        if not historico.pk and not historico.cod_protocolo and not historico.titulo:
                            continue
                        historico.save()
                    
                    # Procesar eliminaciones explícitas (en caso de que el usuario borre filas en el cliente)
                    for obj in formset.deleted_objects:
                        obj.delete()
                        
                    formset.save_m2m()
                    
                    # Registro de auditoría
                    LogEntry.objects.create(
                        user_id=request.user.id,
                        content_type_id=ContentType.objects.get_for_model(ProtocolosDB).id,
                        object_id=protocolo_guardado.id,
                        object_repr=str(protocolo_guardado),
                        action_flag=ADDITION,
                        change_message="Creó un nuevo protocolo en el sistema."
                    )
                    
                    messages.success(request, "¡Protocolo registrado con éxito!")
                    if request.POST.get('query_string'):
                        return redirect(reverse('listado_protocolos') + '?' + request.POST.get('query_string'))
                    return redirect('listado_protocolos')
                    
            except IntegrityError as e:
                logger.error(f"Error de integridad al crear protocolo: {str(e)}")
                messages.error(request, "Error: El ID o código ingresado ya se encuentra en uso.")
    else:
        formulario = ProtocoloForm()
        formset = ProtocolosHistoricoFormSet(instance=None)
        
    context = {
        'formulario': formulario,
        'formset': formset,
        'titulo': "SIGEDOC - Registrar Nuevo Protocolo",
        'query_string': query_string,
    }
    return render(request, 'protocolos/crear.html', context)


# =================================================================
# VISTA: EDITAR PROTOCOLO (CORREGIDA)
# =================================================================
@login_required
def editar_protocolos(request, id):
    protocolo = get_object_or_404(ProtocolosDB, id=id)
    query_string = request.GET.get('query_string', '')
    
    # 1.- FORZAR QUE SOLO APAREZCA UN ÚNICO REGISTRO EN BLANCO
    ProtocolosHistoricoFormSet.extra = 1
    
    if request.method == 'POST':
        # SE AGREGA request.FILES PARA PROCESAR NUEVOS ARCHIVOS O DESVINCULACIONES
        formulario = ProtocoloForm(request.POST, request.FILES, instance=protocolo)
        formset = ProtocolosHistoricoFormSet(request.POST, request.FILES, instance=protocolo)
        
        if formulario.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    original = ProtocolosDB.objects.get(id=id)
                    
                    # Solo se genera histórico si cambió el código del protocolo
                    if original.cod_protocolo != formulario.cleaned_data.get('cod_protocolo'):
                        ProtocolosHistoricoDB.objects.create(
                            protocolo=original,
                            cod_protocolo=original.cod_protocolo,
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

                    protocolo_actualizado = formulario.save()
                    
                    # 2.- CONTROL DE SUBFORMULARIO: FILTRADO SEGURO DE REGISTROS EN BLANCO
                    formset.instance = protocolo_actualizado
                    historicos = formset.save(commit=False)
                    for historico in historicos:
                        # Si es un registro nuevo y no se rellenaron los campos clave, se ignora automáticamente
                        if not historico.pk and not historico.cod_protocolo and not historico.titulo:
                            continue
                        historico.save()
                    
                    # Procesar eliminaciones explícitas de registros existentes
                    for obj in formset.deleted_objects:
                        obj.delete()
                        
                    formset.save_m2m()
                    
                    LogEntry.objects.create(
                        user_id=request.user.id,
                        content_type_id=ContentType.objects.get_for_model(ProtocolosDB).id,
                        object_id=protocolo_actualizado.id,
                        object_repr=str(protocolo_actualizado),
                        action_flag=CHANGE,
                        change_message=f"Modificó datos principales. Se generó histórico automático: {original.cod_protocolo} -> {formulario.cleaned_data.get('cod_protocolo')}"
                    )
                    
                    messages.success(request, "¡Protocolo e Historial actualizados correctamente!")
                    if request.POST.get('query_string'):
                        return redirect(reverse('listado_protocolos') + '?' + request.POST.get('query_string'))
                    return redirect('listado_protocolos')
                    
            except IntegrityError as e:
                logger.error(f"Error de integridad al editar protocolo {id}: {str(e)}")
                messages.error(request, "Error de consistencia en la base de datos al guardar los cambios.")
    else:
        formulario = ProtocoloForm(instance=protocolo)
        formset = ProtocolosHistoricoFormSet(instance=protocolo)
        
    context = {
        'formulario': formulario,
        'formset': formset,
        'titulo': "SIGEDOC - Editar Protocolo",
        'query_string': query_string,
    }
    return render(request, 'protocolos/editar.html', context)

#------------------------------------------
@login_required
def borrar_protocolos(request, id):
    protocolo = get_object_or_404(ProtocolosDB, id=id) 
    identificador = f"Cod. Protocolo {protocolo.cod_protocolo}"
    query_string = request.POST.get('query_string', request.GET.urlencode())

    try:
        protocolo.delete() # Al borrar el protocolo, se borran en cascada sus históricos por el on_delete=models.CASCADE
        
        LogEntry.objects.create(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(ProtocolosDB).id,
            object_id=id, 
            object_repr=f"{identificador} (Borrado)",
            action_flag=DELETION,
            change_message=f'Protocolo {identificador} y su historial eliminados.'
        )
        messages.success(request, f'{identificador} fue eliminado exitosamente', extra_tags='procesado ✅')
        
    except ProtectedError as e:
        logger.error(f"Intento fallido de borrar Protocolo ID {id}: {e}")       
        messages.error(request, "ERROR: No se puede eliminar este protocolo porque está referenciado en otra sección del sistema.", extra_tags='error ❌')
        
    base_url = reverse('listado_protocolos') 
    if query_string:
        return redirect(f'{base_url}?{query_string}')
    return redirect('listado_protocolos')


# ---------------------------------------------------------------------------------
# REPORTE PDF
# ---------------------------------------------------------------------------------
@login_required
def reporte_protocolos_pdf(request):
    search_query = request.GET.get('search_query')
    order_by = request.GET.get('order_by', 'id')

    queryset = ProtocolosDB.objects.all().prefetch_related('historicos')
    if search_query:
        queryset = queryset.filter(
            Q(historicos__cod_actual__icontains=search_query) | 
            Q(historicos__titulo_actual__icontains=search_query)
        ).distinct()

    protocolos = queryset.order_by(order_by)

    def link_callback(uri, rel):
        if uri.startswith(settings.STATIC_URL):
            path = uri.replace(settings.STATIC_URL, "")
            result = finders.find(path)
            if result:
                return result
        return uri

    context = {
        'protocolos': protocolos,
        'titulo_reporte': 'Reporte de Protocolos',
        'logo_path': f"{settings.STATIC_URL}img/logo2.png",
        'fecha_emision': datetime.now(),
    }
    
    template = get_template('reportes/reporte_protocolos_pdf.html')
    html = template.render(context)
    result = BytesIO()
    
    pisa_status = pisa.CreatePDF(html, dest=result, encoding='utf-8', link_callback=link_callback)
    if pisa_status.err: 
        return HttpResponse('Error al generar el PDF', status=500)
        
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Reporte_Protocolos.pdf"'
    return response


