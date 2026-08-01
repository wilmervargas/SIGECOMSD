from django.urls import path
from . import views

urlpatterns = [
    path('', views.panel_control, name='dashboard')
]