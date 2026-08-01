
# manuales/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # CORRECCIÓN CLAVE: El listado debe estar en la cadena vacía
    # Esto coincide con /procedimientos/
    path('', views.listado_procedimientos, name='listado_procedimientos'),
    path('crear/', views.crear_procedimientos, name='crear_procedimientos'), 
    path('editar/<int:id>/', views.editar_procedimientos, name='editar_procedimientos'),
    path('borrar/<int:id>/', views.borrar_procedimientos, name='borrar_procedimientos'),
    path('reporte/procedimientos/pdf/', views.reporte_procedimientos_pdf, name='reporte_procedimientos_pdf'),
]   
