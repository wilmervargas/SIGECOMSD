
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
from .models import FormulariosDB, FormulariosHistoricoDB
from .forms import FormularioForm, FormulariosHistoricoForm, FormularioFilterForm, FormulariosHistoricoFormSet
from dependencias.models import DependenciasBD

logger = logging.getLogger(__name__)

# =================================================================
# VISTA PRINCIPAL DE FORMULARIOS CON FILTROS Y ORDENACIÓN
# =================================================================
@login_required
def listado_formularios(request):
    filter_form = FormularioFilterForm(request.GET)
    # Optimizamos la consulta con select_related y prefetch_related para el histórico
    queryset_formularios = FormulariosDB.objects.all().select_related('cod_dependencia').prefetch_related('historicos')

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
            queryset_formularios = queryset_formularios.filter(
                Q(historicos__cod_actual__icontains=search_query) | 
                Q(historicos__titulo_actual__icontains=search_query)
            ).distinct()

    # Ordenación por ID o por el campo seleccionado
    order_by_principal = request.GET.get('order_by', 'id') 
    campos_ordenar = [order_by_principal]
    
    lista_formularios = queryset_formularios.order_by(*campos_ordenar) 

    # Paginación
    page_number = request.GET.get('page', 1)
    paginator = Paginator(lista_formularios, 50)  # Cambiado a 50 registros por página
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    except Exception:
        raise Http404('*** Página no encontrada ***')

    datos = {
        'titulo': 'Tabla Maestro de Formularios',
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
    return render(request, 'formularios/listado.html', datos)


# =================================================================
# VISTA: CREAR FORMULARIO (CORREGIDA CON ADAPTACIÓN DE SUBFORMULARIO)
# =================================================================
@login_required
def crear_formularios(request):
    query_string = request.GET.get('query_string', '')
    
    # 1.- FORZAR QUE SOLO APAREZCA UN ÚNICO REGISTRO EN BLANCO EN EL DETALLE
    FormulariosHistoricoFormSet.extra = 1
    
    if request.method == 'POST':
        # SE AGREGA request.FILES PARA CAPTURAR LOS ARCHIVOS SUBIDOS
        formulario = FormularioForm(request.POST, request.FILES)
        formset = FormulariosHistoricoFormSet(request.POST, request.FILES, instance=None)
        
        if formulario.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Guardar el encabezado primero para obtener el ID principal
                    formulario_guardado = formulario.save()
                    
                    # 2.- CONTROL DE SUBFORMULARIO: FILTRADO SEGURO DE REGISTROS EN BLANCO
                    formset.instance = formulario_guardado
                    historicos = formset.save(commit=False)
                    for historico in historicos:
                        # Si es una fila nueva y viene vacía en los campos clave, se ignora y no se guarda
                        if not historico.pk and not historico.cod_formulario and not historico.titulo:
                            continue
                        historico.save()
                    
                    # Procesar eliminaciones explícitas (en caso de que el usuario borre filas en el cliente)
                    for obj in formset.deleted_objects:
                        obj.delete()
                        
                    formset.save_m2m()
                    
                    # Registro de auditoría
                    LogEntry.objects.create(
                        user_id=request.user.id,
                        content_type_id=ContentType.objects.get_for_model(FormulariosDB).id,
                        object_id=formulario_guardado.id,
                        object_repr=str(formulario_guardado),
                        action_flag=ADDITION,
                        change_message="Creó un nuevo formulario en el sistema."
                    )
                    
                    messages.success(request, "¡Formulario registrado con éxito!")
                    if request.POST.get('query_string'):
                        return redirect(reverse('listado_formularios') + '?' + request.POST.get('query_string'))
                    return redirect('listado_formularios')
                    
            except IntegrityError as e:
                logger.error(f"Error de integridad al crear formulario: {str(e)}")
                messages.error(request, "Error: El ID o código ingresado ya se encuentra en uso.")
    else:
        formulario = FormularioForm()
        formset = FormulariosHistoricoFormSet(instance=None)
        
    context = {
        'formulario': formulario,
        'formset': formset,
        'titulo': "SIGEDOC - Registrar Nuevo Formulario",
        'query_string': query_string,
    }
    return render(request, 'formularios/crear.html', context)


# =================================================================
# VISTA: EDITAR FORMULARIO (CORREGIDA)
# =================================================================
# =================================================================
# VISTA: EDITAR FORMULARIO (CORREGIDA)
# =================================================================
@login_required
def editar_formularios(request, id):
    # Cambiamos el nombre de la variable para que no choque con el FormularioForm
    objeto_formulario = get_object_or_404(FormulariosDB, id=id)
    query_string = request.GET.get('query_string', '')
    
    # 1.- FORZAR QUE SOLO APAREZCA UN ÚNICO REGISTRO EN BLANCO
    FormulariosHistoricoFormSet.extra = 1
    
    if request.method == 'POST':
        # Pasamos "objeto_formulario" como la instancia del modelo
        formulario = FormularioForm(request.POST, request.FILES, instance=objeto_formulario)
        formset = FormulariosHistoricoFormSet(request.POST, request.FILES, instance=objeto_formulario)
        
        if formulario.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    original = FormulariosDB.objects.get(id=id)
                    
                    # Solo se genera histórico si cambió el código del formulario
                    if original.cod_formulario != formulario.cleaned_data.get('cod_formulario'):
                        FormulariosHistoricoDB.objects.create(
                            formulario=original,
                            cod_formulario=original.cod_formulario,
                            titulo=original.titulo,
                            fecha_elaboracion=original.fecha_elaboracion,
                            fecha_revision=original.fecha_revision,
                            fecha_aprobacion=original.fecha_aprobacion,
                            version=original.version,
                            distribucion_digital=original.distribucion_digital,
                            distribucion_fisica=original.distribucion_fisica,
                            observaciones=original.observaciones,
                            archivo_pdf=original.archivo_pdf
                        )

                    formulario_actualizado = formulario.save()
                    
                    # 2.- CONTROL DE SUBFORMULARIO: FILTRADO SEGURO DE REGISTROS EN BLANCO
                    formset.instance = formulario_actualizado
                    historicos = formset.save(commit=False)
                    for historico in historicos:
                        if not historico.pk and not historico.cod_formulario and not historico.titulo:
                            continue
                        historico.save()
                    
                    # Procesar eliminaciones explícitas de registros existentes
                    for obj in formset.deleted_objects:
                        obj.delete()
                        
                    formset.save_m2m()
                    
                    LogEntry.objects.create(
                        user_id=request.user.id,
                        content_type_id=ContentType.objects.get_for_model(FormulariosDB).id,
                        object_id=formulario_actualizado.id,
                        object_repr=str(formulario_actualizado),
                        action_flag=CHANGE,
                        change_message=f"Modificó datos principales. Se generó histórico automático: {original.cod_formulario} -> {formulario.cleaned_data.get('cod_formulario')}"
                    )
                    
                    messages.success(request, "¡Formulario e Historial actualizados correctamente!")
                    if request.POST.get('query_string'):
                        return redirect(reverse('listado_formularios') + '?' + request.POST.get('query_string'))
                    return redirect('listado_formularios')
                    
            except IntegrityError as e:
                logger.error(f"Error de integridad al editar formulario {id}: {str(e)}")
                messages.error(request, "Error de consistencia en la base de datos al guardar los cambios.")
    else:
        # Aquí se evita el solapamiento:
        # "formulario" es el FormularioForm e "instance" recibe el modelo "objeto_formulario"
        formulario = FormularioForm(instance=objeto_formulario)
        formset = FormulariosHistoricoFormSet(instance=objeto_formulario)
        
    context = {
        'formulario': formulario,
        'formset': formset,
        'titulo': "SIGEDOC - Editar Formulario",
        'query_string': query_string,
    }
    return render(request, 'formularios/editar.html', context)
    
#------------------------------------------
@login_required
def borrar_formularios(request, id):
    formulario = get_object_or_404(FormulariosDB, id=id) 
    identificador = f"Formulario N° {formulario.id}"
    query_string = request.POST.get('query_string', request.GET.urlencode())

    try:
        formulario.delete() # Al borrar el formulario, se borran en cascada sus históricos por el on_delete=models.CASCADE
        
        LogEntry.objects.create(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(FormulariosDB).id,
            object_id=id, 
            object_repr=f"{identificador} (Borrado)",
            action_flag=DELETION,
            change_message=f'Formulario {identificador} y su historial eliminados.'
        )
        messages.success(request, f'{identificador} fue eliminado exitosamente', extra_tags='procesado ✅')
        
    except ProtectedError as e:
        logger.error(f"Intento fallido de borrar Formulario ID {id}: {e}")       
        messages.error(request, "ERROR: No se puede eliminar este formulario porque está referenciado en otra sección del sistema.", extra_tags='error ❌')
        
    base_url = reverse('listado_formularios') 
    if query_string:
        return redirect(f'{base_url}?{query_string}')
    return redirect('listado_formularios')


# ---------------------------------------------------------------------------------
# REPORTE PDF
# ---------------------------------------------------------------------------------
@login_required
def reporte_formularios_pdf(request):
    search_query = request.GET.get('search_query')
    order_by = request.GET.get('order_by', 'id')

    queryset = FormulariosDB.objects.all().prefetch_related('historicos')
    if search_query:
        queryset = queryset.filter(
            Q(historicos__cod_actual__icontains=search_query) | 
            Q(historicos__titulo_actual__icontains=search_query)
        ).distinct()

    formularios = queryset.order_by(order_by)

    def link_callback(uri, rel):
        if uri.startswith(settings.STATIC_URL):
            path = uri.replace(settings.STATIC_URL, "")
            result = finders.find(path)
            if result:
                return result
        return uri

    context = {
        'formularios': formularios,
        'titulo_reporte': 'Reporte de Formularios',
        'logo_path': f"{settings.STATIC_URL}img/membrete.png",
        'fecha_emision': datetime.now(),
    }
    
    template = get_template('reportes/reporte_formularios_pdf.html')
    html = template.render(context)
    result = BytesIO()
    
    pisa_status = pisa.CreatePDF(html, dest=result, encoding='utf-8', link_callback=link_callback)
    if pisa_status.err: 
        return HttpResponse('Error al generar el PDF', status=500)
        
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Reporte_Formularios.pdf"'
    return response


