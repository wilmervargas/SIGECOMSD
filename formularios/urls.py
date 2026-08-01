
# manuales/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # CORRECCIÓN CLAVE: El listado debe estar en la cadena vacía
    # Esto coincide con /formularios/
    path('', views.listado_formularios, name='listado_formularios'),
    path('crear/', views.crear_formularios, name='crear_formularios'), 
    path('editar/<int:id>/', views.editar_formularios, name='editar_formularios'),
    path('borrar/<int:id>/', views.borrar_formularios, name='borrar_formularios'),
    path('reporte/formularios/pdf/', views.reporte_formularios_pdf, name='reporte_formularios_pdf'),
]   
