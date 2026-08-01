
# manuales/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # CORRECCIÓN CLAVE: El listado debe estar en la cadena vacía
    # Esto coincide con /manuales/
    path('', views.listado_manuales, name='listado_manuales'),
    path('crear/', views.crear_manuales, name='crear_manuales'), 
    path('editar/<int:id>/', views.editar_manuales, name='editar_manuales'),
    path('borrar/<int:id>/', views.borrar_manuales, name='borrar_manuales'),
    path('reporte/manuales/pdf/', views.reporte_manuales_pdf, name='reporte_manuales_pdf'),
]   
