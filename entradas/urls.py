# entradas/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # CORRECCIÓN CLAVE: El listado debe estar en la cadena vacía
    # Esto coincide con /entradas/
    path('', views.listado_entradas, name='listado_entradas'),
    path('crear/', views.crear_entradas, name='crear_entradas'), 
    path('editar/<int:id>/', views.editar_entradas, name='editar_entradas'),
    path('borrar/<int:id>/', views.borrar_entradas, name='borrar_entradas'),
    path('imprimir/<int:id>/', views.imprimir_entradas, name='imprimir_entradas'),
    path('reporte/entradas/pdf/', views.reporte_entradas_pdf, name='reporte_entradas_pdf'),
    path('reporte/entradas/excel/', views.reporte_entradas_excel, name='reporte_entradas_excel'), 
    path('revertir-anulacion-entrada/', views.revertir_anulacion_entrada_ajax, name='revertir_anulacion_entrada_ajax'),
    path('desbloquear-entrada/', views.desbloquear_entrada_ajax, name='desbloquear_entrada_ajax'),
    path('ejecutar-anulacion-entrada/', views.ejecutar_anulacion_entrada_ajax, name='ejecutar_anulacion_entrada_ajax'),
    
]   
