# salidas/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # CORRECCIÓN CLAVE: El listado debe estar en la cadena vacía
    # Esto coincide con /salidas/
    path('', views.listado_salidas, name='listado_salidas'),
    path('crear/', views.crear_salidas, name='crear_salidas'), 
    path('editar/<int:id>/', views.editar_salidas, name='editar_salidas'),
    path('borrar/<int:id>/', views.borrar_salidas, name='borrar_salidas'),
    path('imprimir/<int:id>/', views.imprimir_requisicion, name='imprimir_requisicion'),
    path('reporte/salidas/pdf/', views.reporte_salidas_pdf, name='reporte_salidas_pdf'),
    path('reporte/salidas/excel/', views.reporte_salidas_excel, name='reporte_salidas_excel'), 
    path('revertir-poraprobar/', views.revertir_poraprobar_ajax, name='revertir_poraprobar_ajax'),
    path('revertir-anulacion/', views.revertir_anulacion_ajax, name='revertir_anulacion_ajax'),
    path('desbloquear/', views.desbloquear_ajax, name='desbloquear_ajax'),
    path('ejecutar-anulacion/', views.ejecutar_anulacion_ajax, name='ejecutar_anulacion_ajax'),
]   
