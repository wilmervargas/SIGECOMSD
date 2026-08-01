from django.db import models
from django.conf import settings
from dependencias.models import DependenciasBD 

class DirectoresBD(models.Model):
    cedula = models.CharField(max_length=15, unique=True, verbose_name="Cédula")
    nombres_apellidos = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombres y Apellidos")
    usuario = models.CharField(max_length=20, default='sin_usuario', null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    def __str__(self):
        return self.nombres_apellidos

class DependeciasDirectorBD(models.Model):
    director = models.ForeignKey(DirectoresBD, on_delete=models.PROTECT, related_name='oficinas')
    # Añadimos related_name='directores_asignados'
    dependencia = models.ForeignKey(DependenciasBD, on_delete=models.PROTECT, related_name='directores_asignados')    
    cargo = models.CharField(max_length=1, choices=[('T', 'Titular'), ('E', 'Encargado')], default='T')
    activo = models.BooleanField(default=True, null=True, verbose_name="¿Activo?")

    class Meta:
        # Evita duplicar al mismo director en la misma oficina
        unique_together = ('director', 'dependencia')