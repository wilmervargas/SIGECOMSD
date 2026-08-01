
# Create your models here.
from django.db import models
from productos.models import Producto
from dependencias.models import DependenciasBD
from directores.models import DirectoresBD, DependeciasDirectorBD

class SalidaEncabezado(models.Model):
    # AutoField hace que sea autoincremental y primary_key elimina la necesidad de un 'id' extra
    num_requi = models.AutoField(primary_key=True, verbose_name="Número de Requis.")

    # Campos actualizados para permitir nulos y vacíos
    fecha_requi = models.DateField(
        verbose_name="Fecha de Requis."
    )
    fecha_aprobacion = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Fecha Aprobación"
    )
    # Relación con dependencia (también permite nulo si no se selecciona uno)
    cod_dependencia_soli = models.ForeignKey(
        DependenciasBD, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        verbose_name="Dependencia"
    )

    ESTADO_CHOICES = [
        ('EN_PROCESO', 'EN_PROCESO'), # <-- Nuevo estado
        ('POR_APROBAR', 'POR_APROBAR'),
        ('PROCESADA', 'PROCESADA'),
        ('ANULADA', 'ANULADA'),]

    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        null=True, 
        blank=True, 
        default='EN_PROCESO',
        verbose_name="Estado de la Requisición"
    )

    class Meta:
        verbose_name_plural = "Salidas (Encabezado)"

class SalidaDetalle(models.Model):
    encabezado = models.ForeignKey(SalidaEncabezado, related_name='detalles', on_delete=models.CASCADE)
    cod_producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cant_solicitada = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    cant_entregada = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    
    @property
    def stock_maestro(self):
        """Retorna la cantidad actual en el inventario real"""
        return self.cod_producto.cantidad if self.cod_producto else 0

    @property
    def existencia_proyectada(self):
        """Suma lógica: lo que hay + lo que está llegando"""
        actual = self.cod_producto.cantidad if self.cod_producto else 0
        entregado = self.cant_entregada or 0
        return actual + entregado
