from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate

# Create your views here.
@login_required
def panel_control(request):
    datos = {
        'titulo': 'Panel de control',
        'subpagina': 'subpage',
    }
    
    return render (request,'dashboard/index.html', datos)
