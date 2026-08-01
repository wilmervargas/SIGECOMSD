from django.shortcuts import render, redirect
from .models import CategoriaBD
from .forms import CategoriaForm

# SEGURIDAD HISTORICO DE LOS REGISTROS
from django.contrib.contenttypes.models import ContentType # Para identificar el modelo
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION      # LogEntry y Flags de acción
# 💡 NUEVA IMPORTACIÓN PARA MANEJO DE ERRORES DE BASE DE DATOS
from django.db import IntegrityError 
# 💡 NUEVA IMPORTACIÓN PARA EL REGISTRO DE EVENTOS (LOGGING)
import logging
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

logger = logging.getLogger(__name__)

# Create your views here.
@login_required
def categoria_lista(request):
    lista_categorias = CategoriaBD.objects.all()
    return render(request, "categorias/gestion_categorias.html", {"categorias":lista_categorias})


def registrar_Categoria(request):
    origen = request.POST.get('origen') or request.GET.get('origen')
    # 1. Inicializa el formulario con datos (si es POST) o sin ellos (si es GET)
    # Nota: Tu formulario espera datos de los campos 'cod_categoria' y 'descripcion',
    #       NO 'txtCodigo'/'txtDescripcion'. Arreglaremos esto en el Formulario HTML.
    formulario = CategoriaForm(request.POST or None) 
    
    if formulario.is_valid():
        try:
            # 🎯 BLOQUE TRY: Usa el formulario para guardar el objeto
            
            # 1. 🟢 Guarda y obtén el objeto creado usando el formulario.save()
            #    commit=True es el valor predeterminado, pero se incluye por claridad.
            categoria = formulario.save(commit=True) 
            
            # 🟢 REGISTRO DE LOG (Creación Exitosa) --------------------------
            # El resto de tu lógica de LogEntry es correcta
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(categoria).pk,
                object_id=categoria.pk, 
                object_repr=str(categoria), 
                action_flag=ADDITION,
                change_message='Categoria creada mediante vista utilizando ModelForm.'
            )
            messages.success(request, 'Categoria creada exitosamente', 
                             extra_tags='procesado ✅')
            
            if origen == 'modal' or origen == '2':
                # Si viene del modal (p. ej., de crear.html), redirigimos 
                # a la vista de categorías CON el parámetro origen, para que 
                # el modal se recargue correctamente y no la página entera.
                # Nota: Si el modal ya está abierto, esta redirección recargará 
                #       SOLO el contenido del modal, que es lo que queremos.
                return redirect(reverse('categoria_lista') + f'?origen={origen}')
            else:
                # Si viene del flujo normal (CRUD), redirigimos al listado.
                return redirect('categoria_lista')
        
        except (OverflowError, IntegrityError, Exception) as e:
            # 🛑 BLOQUE EXCEPT: Tu lógica de manejo de errores está bien.
            logger.error(f"Fallo crítico al crear categoria para usuario {request.user.pk}: {e}", exc_info=True)
            
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(CategoriaBD).pk,
                object_id=None,
                object_repr='Fallo en la creación de categoria', 
                action_flag=4,
                change_message=f'ERROR CRÍTICO: No se pudo crear la categoria. Causa: {type(e).__name__}. Ver log del servidor.'
            )
            
            messages.error(request, 'Error grave de ejecución. La categoria NO fue creada. Por favor, contacte a soporte.', extra_tags='error ❌')

            if origen == 'modal' or origen == '2':
                return redirect(reverse('categoria_lista') + f'?origen={origen}')
            else:
                return redirect('categoria_lista')

    # Si la solicitud es GET o el formulario NO es válido (POST fallido), 
    # la función sigue ejecutándose aquí. Renderizamos la plantilla con el formulario.
    # Necesitas que la vista que lista las categorías pase las categorías, y esta vista
    # no lo hace. Esto podría causar un error de contexto.

    # 💡 RECOMENDACIÓN: Mover el formulario a una vista separada (opcional, pero mejor)
    # Por ahora, mantendremos la estructura original de redirección al final del error.
    
    # Si la rutina llega aquí, generalmente es un GET o un POST inválido.
    # Dado que la plantilla gestion_categorias.html necesita el contexto 'categorias',
    # es mejor mover esta lógica a la vista principal (categoria_lista) o
    # redirigir. Ya estás redirigiendo, por lo que este render final es inútil 
    # si la validación falla:
    # return render(request, 'categorias/gestion_categorias.html') # <-- ELIMINAR

    # **SOLUCIÓN CONSERVADORA:** Si el formulario falla, redirige para mostrar el mensaje de error
    # y que la página cargue el listado correctamente.
    return redirect('categoria_lista')

def eliminar_Categoria(request, pk):
    categoria = CategoriaBD.objects.get(pk=pk)

    # 🟢 REGISTRO DE LOG (Eliminación Exitosa) -------------------------    
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(categoria).pk,
        object_id=categoria.pk, 
        object_repr=str(categoria), 
        action_flag=DELETION,
        change_message='Categoria eliminada mediante vista.'
    )

    categoria.delete()
    messages.success(request, 'Categoria eliminada exitosamente', 
                     extra_tags='procesado ✅') 
    return redirect('categoria_lista')

def editar_Categoria(request):
    pass
