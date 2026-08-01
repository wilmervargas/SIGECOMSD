"""
URL configuration for maininv project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# my_alpha_project/urls.py
from django.contrib import admin
from django.urls import path, include
#from home import views  # <-- Asegúrate de que tu app 'core' esté importada
# PASO A: Importar las configuraciones necesarias
from django.conf import settings
from django.conf.urls.static import static
from productos import views # Suponiendo esto

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ESTA LÍNEA ES LA CLAVE:
    path('', include('home.urls')), 
    path('login/', include('login.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('productos/', include('productos.urls')),
    path('categorias/', include('categorias.urls')),
    path('unidades/', include('unidades.urls')),
    path('dependencias/', include('dependencias.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('directores/', include('directores.urls')),
    path('entradas/', include('entradas.urls')),
    path('salidas/', include('salidas.urls')),
    path('estadisticas/', include('estadisticas.urls')),
    path('manuales/', include('manuales.urls')),
    path('procedimientos/', include('procedimientos.urls')),
    path('protocolos/', include('protocolos.urls')),
    path('formularios/', include('formularios.urls')),
    path('baselegal/', include('baselegal.urls')),
]

# 🚨 IMPORTANTE: Solo para entorno de desarrollo 🚨
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


