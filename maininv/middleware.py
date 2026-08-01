from django.shortcuts import redirect
from django.urls import reverse, resolve, NoReverseMatch

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Si el usuario ya está logueado, dejarlo pasar
        if request.user.is_authenticated:
            return self.get_response(request)

        # 2. Definir las rutas permitidas (Excepciones)
        try:
            # Intentamos obtener el nombre de la ruta actual
            current_url_name = resolve(request.path_info).url_name
        except:
            current_url_name = None

        # Lista de nombres de URL que NO requieren login
        exempt_names = ['home', 'login']
        
        # 3. Verificación
        # Si es la raíz '/', si es el admin, o si el nombre está en la lista de permitidos
        if request.path == '/' or request.path.startswith('/admin/') or current_url_name in exempt_names:
            return self.get_response(request)

        # 4. Si no es nada de lo anterior y no está logueado, al login
        return redirect('login')