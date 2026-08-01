from django.db import models

# Create your models here.
class UnidadBD(models.Model):
    """Clasificación de Unidad."""
    cod_unidad = models.CharField(max_length=20, unique=True, verbose_name="Codigo de Unidad")
    descripcion = models.TextField(blank=False, null=True, verbose_name="Descripción")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    def __str__(self):
        return self.descripcion

    class Meta:
        verbose_name_plural = "Unidad"

