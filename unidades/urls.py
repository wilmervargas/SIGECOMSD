
from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_unidad, name='listado_unidad'),
    path('crear/', views.crear_unidad, name='crear_unidad'), 
    path('editar/<int:id>/', views.editar_unidad, name='editar_unidad'),
    path('borrar/<int:id>/', views.borrar_unidad, name='borrar_unidad'),
    path('reporte/unidades/pdf/', views.reporte_unidades_pdf, name='reporte_unidades_pdf'),
    path('reporte/unidades/excel/', views.reporte_unidades_excel, name='reporte_unidades_excel'), 

]   
