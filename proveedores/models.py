from django.db import models

# Create your models here.
class ProveedoresBD(models.Model):
    """Clasificación de los Artículos Base."""
    ced_proveedor = models.CharField(max_length=15, unique=True, verbose_name="Céd Proveedor/RIF")
    nombres_apellidos = models.TextField(blank=False, null=True, verbose_name="Nombres y Apellidos/Razón Social")
    cedula_representante = models.TextField(blank=True, null=True, verbose_name="Cédula Representante")
    nombres_representante = models.TextField(blank=True, null=True, verbose_name="Nombres Representante")
    rif = models.TextField(blank=True, null=True, verbose_name="RIF")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    telefonos = models.TextField(blank=True, null=True, verbose_name="Teléfonos]")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    def __str__(self):
        return self.nombres_apellidos
    
    class Meta:
        verbose_name_plural = "Proveedores"

