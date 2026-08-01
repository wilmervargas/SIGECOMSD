from django.db import models

# Create your models here.
class DependenciasBD(models.Model):
    """Clasificación de los Artículos Base."""
    cod_dependencia = models.CharField(max_length=15, unique=True, verbose_name="Cod Dependencia")
    descripcion = models.TextField(blank=False, null=True, verbose_name="Descripcion")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    def __str__(self):
        return self.descripcion
    
    class Meta:
        verbose_name_plural = "Dependencias"
        ordering = ['cod_dependencia'] # Ordena de forma ascendente por defecto
