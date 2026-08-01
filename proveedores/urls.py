
from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_proveedores, name='listado_proveedores'),
    path('crear/', views.crear_proveedores, name='crear_proveedores'), 
    path('editar/<int:id>/', views.editar_proveedores, name='editar_proveedores'),
    path('borrar/<int:id>/', views.borrar_proveedores, name='borrar_proveedores'),
    path('reporte/proveedores/pdf/', views.reporte_proveedores_pdf, name='reporte_proveedores_pdf'),
    path('reporte/proveedores/excel/', views.reporte_proveedores_excel, name='reporte_proveedores_excel'), 

]   
