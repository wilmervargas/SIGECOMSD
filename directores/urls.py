
from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_directores, name='listado_directores'),
    path('crear/', views.crear_directores, name='crear_directores'), 
    path('editar/<int:id>/', views.editar_directores, name='editar_directores'),
    path('borrar/<int:id>/', views.borrar_directores, name='borrar_directores'),
    path('reporte/directores/pdf/', views.reporte_directores_pdf, name='reporte_directores_pdf'),
    path('reporte/directores/excel/', views.reporte_directores_excel, name='reporte_directores_excel'), 

]   
