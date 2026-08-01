
from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_categoria, name='listado_categoria'),
    path('crear/', views.crear_categoria, name='crear_categoria'), 
    path('editar/<int:id>/', views.editar_categoria, name='editar_categoria'),
    path('borrar/<int:id>/', views.borrar_categoria, name='borrar_categoria'),
    path('reporte/categorias/pdf/', views.reporte_categorias_pdf, name='reporte_categorias_pdf'),
    path('reporte/categorias/excel/', views.reporte_categorias_excel, name='reporte_categorias_excel'), 

]   
