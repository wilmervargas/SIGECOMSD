
from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_dependencias, name='listado_dependencias'),
    path('crear/', views.crear_dependencias, name='crear_dependencias'), 
    path('editar/<int:id>/', views.editar_dependencias, name='editar_dependencias'),
    path('borrar/<int:id>/', views.borrar_dependencias, name='borrar_dependencias'),
    path('reporte/dependencias/pdf/', views.reporte_dependencias_pdf, name='reporte_dependencias_pdf'),
    path('reporte/dependencias/excel/', views.reporte_dependencias_excel, name='reporte_dependencias_excel'), 

]   
