
# manuales/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # CORRECCIÓN CLAVE: El listado debe estar en la cadena vacía
    # Esto coincide con /baselegal/
    path('', views.listado_baselegal, name='listado_baselegal'),
    path('crear/', views.crear_baselegal, name='crear_baselegal'), 
    path('editar/<int:id>/', views.editar_baselegal, name='editar_baselegal'),
    path('borrar/<int:id>/', views.borrar_baselegal, name='borrar_baselegal'),
    path('reporte/baselegal/pdf/', views.reporte_baselegal_pdf, name='reporte_baselegal_pdf'),
]   
