# estadisticas/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # CORRECCIÓN CLAVE: El listado debe estar en la cadena vacía
    # Esto coincide con /estadisticas/
    path('', views.listado_ranking_salidas, name='listado_ranking_salidas'),
    path('reporte/ranking_salidas/pdf/', views.reporte_ranking_salidas_pdf, name='reporte_ranking_salidas_pdf'),
]   
