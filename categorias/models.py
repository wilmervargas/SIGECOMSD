from django.db import models

# Create your models here.
class CategoriaBD(models.Model):
    """Clasificación de los Artículos Base."""
    cod_categoria = models.CharField(max_length=20, unique=True, verbose_name="Codigo de Categoría")
    descripcion = models.TextField(blank=False, null=True, verbose_name="Descripción")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    def __str__(self):
        return self.descripcion
    
    class Meta:
        verbose_name_plural = "Categorías"

