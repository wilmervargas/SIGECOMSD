# productos/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # CORRECCIÓN CLAVE: El listado debe estar en la cadena vacía
    # Esto coincide con /productos/
    path('', views.listado_productos, name='listado_productos'),
    path('crear/', views.crear_productos, name='crear_productos'), 
    path('editar/<int:id>/', views.editar_productos, name='editar_productos'),
    path('borrar/<int:id>/', views.borrar_productos, name='borrar_productos'),
    path('reporte/productos/pdf/', views.reporte_productos_pdf, name='reporte_productos_pdf'),
    path('reporte/productos/excel/', views.reporte_productos_excel, name='reporte_productos_excel'), 
    
]   
