
# manuales/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # CORRECCIÓN CLAVE: El listado debe estar en la cadena vacía
    # Esto coincide con /protocolos/
    path('', views.listado_protocolos, name='listado_protocolos'),
    path('crear/', views.crear_protocolos, name='crear_protocolos'), 
    path('editar/<int:id>/', views.editar_protocolos, name='editar_protocolos'),
    path('borrar/<int:id>/', views.borrar_protocolos, name='borrar_protocolos'),
    path('reporte/protocolos/pdf/', views.reporte_protocolos_pdf, name='reporte_protocolos_pdf'),
]   
