
# Create your models here.
from django.db import models
from productos.models import Producto
from proveedores.models import ProveedoresBD

class EntradaEncabezado(models.Model):
    # AutoField hace que sea autoincremental y primary_key elimina la necesidad de un 'id' extra
    num_orden = models.AutoField(primary_key=True, verbose_name="Número de Orden")
    
    # Campos actualizados para permitir nulos y vacíos
    fecha_orden = models.DateField(
        verbose_name="Fecha de Ingreso"
    )
    num_factura = models.CharField(
        max_length=50, 
        null=True, 
        blank=True, 
        verbose_name="Número de Factura"
    )
    fecha_factura = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Fecha de Factura"
    )
    monto_factura = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Monto Factura"
    )
    
    # Relación con Proveedor (también permite nulo si no se selecciona uno)
    ced_proveedor = models.ForeignKey(
        ProveedoresBD, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        verbose_name="Proveedor"
    )

    ESTADO_CHOICES = [
        ('EN_PROCESO', 'EN_PROCESO'), # <-- Nuevo estado
        ('PROCESADA', 'PROCESADA'),
        ('ANULADA', 'ANULADA'),]

    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        null=True, 
        blank=True, 
        default='EN_PROCESO',
        verbose_name="Estado de la Orden"
    )

    class Meta:
        verbose_name_plural = "Entradas (Encabezado)"

class EntradaDetalle(models.Model):
    encabezado = models.ForeignKey(EntradaEncabezado, related_name='detalles', on_delete=models.CASCADE)
    cod_producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cant_recibida = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    
    @property
    def stock_maestro(self):
        """Retorna la cantidad actual en el inventario real"""
        return self.cod_producto.cantidad if self.cod_producto else 0

    @property
    def existencia_proyectada(self):
        """Suma lógica: lo que hay + lo que está llegando"""
        actual = self.cod_producto.cantidad if self.cod_producto else 0
        recibido = self.cant_recibida or 0
        return actual + recibido
