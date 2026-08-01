from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate

# Create your views here.
def inicio_sesion(request):
    #print(f'Datos enviados por POST: {request.POST}')
    datos = {
        'titulo': 'Inicio de sesion',
        'subpagina': 'subpage',
    }
    if request.method =='GET':
        return render (request, 'login/index.html', datos)
    else:
        user = authenticate(request, 
                            username=request.POST['username'],
                            password=request.POST['password'],
                            )   
    if user is None:   
        error = {
            'titulo': 'Inicio de sesion',
            'subpagina': 'subpage',
            'msj': 'Estas credenciales no coinciden con nuestro registro',
        }     
        return render (request, 'login/index.html', error)
    else:
        login(request, user)
        return redirect('dashboard')
    
def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')