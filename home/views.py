from django.shortcuts import render, redirect # Importar redirect para una mejor práctica
import os
from django.conf import settings
import random
from django.core.mail import send_mail
from django.http import HttpResponse

# Create your views here.

def home(request):
    # --- Lógica para obtener dinámicamente las imágenes del banner (Mantenida) ---
    image_list = []
    
    try:
        STATIC_DIR = settings.STATICFILES_DIRS[0]
        IMGS_DIR = os.path.join(STATIC_DIR, 'img')
        all_files = os.listdir(IMGS_DIR)
        image_list = [
            f for f in all_files 
            if f.lower().endswith(('.jpg', '.jpeg'))
        ]
    except Exception as e:
        pass

    # Se inicializa 'datos' antes de usarlo en el manejo del POST
    random.shuffle(image_list)
    datos = {
        'titulo': 'Inven ',
        'subpagina': '',
        'imagenes_del_banner': image_list,
    }

    # --- Lógica de Manejo del Formulario de Contacto (AÑADIDA) ---
    if request.method == 'POST':
        # Captura los datos del formulario (usando los IDs del index.html)
        name = request.POST.get('name') 
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Define el contenido del correo a enviar
        contact_subject = f"Mensaje de Contacto: {subject}"
        contact_message = f"De: {name}\nCorreo: {email}\n\nMensaje:\n{message}"
        
        # El correo DESTINO DE LOS MENSAJES (debes cambiarlo)
        recipient_list = ['mail@demo.com'] # Dirección placeholder del index.html

        try:
            send_mail(
                contact_subject,
                contact_message,
                settings.EMAIL_HOST_USER, # Remitente configurado en settings.py
                recipient_list,           # Lista de destinatarios
                fail_silently=False,
            )
            # Mensaje de éxito para mostrar al usuario
            datos['mensaje_exito'] = '¡Tu mensaje ha sido enviado exitosamente!'
        
        except Exception as e:
            # Mensaje de error (útil para depurar)
            datos['mensaje_error'] = 'Hubo un error al enviar el mensaje. Asegúrate de que tu configuración de EMAIL en settings.py sea correcta.'
    
    # Renderiza la plantilla con los datos y el posible mensaje de éxito/error
    return render(request, 'home/index.html', datos)

