from django.db import models
from django.utils import timezone
from categorias.models import CategoriaBD
from unidades.models import UnidadBD

# =========================================================
# MODELO PRINCIPAL: PRODUCTO (Actualizado)
# =========================================================

class Producto(models.Model):
    # --- Identificación y Descripción ---
    cod_producto = models.CharField(max_length=20, unique=True, verbose_name='Código')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción Detallada')
    activo = models.BooleanField(default=True, verbose_name='Insumo Activo')
    
    # --- Relaciones ---
    cod_unidad = models.ForeignKey(UnidadBD, on_delete=models.PROTECT, null=True, verbose_name='Unidad')
    cod_categoria = models.ForeignKey(CategoriaBD, on_delete=models.PROTECT, null=True, verbose_name='Categoría')
    
    # NOTA: Se ELIMINAN cod_almacen, cod_ubicacion y stock_actual.

    # --- Control de Stock (Global/Alerta) ---
    stock_minimo_global = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name='Stock Mín Global') # Campo renombrado
    stock_maximo = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name='Stock Máximo')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Cant. Actual')
    
    # --- Precios y Finanzas ---
    costo_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Costo Compra Unit')
    #precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Precio Venta Unit')
    #total_inversion = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Total Inversión')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones') # Reposicionado aquí

    # --- Trazabilidad y Estado ---
    imagen = models.ImageField(
        upload_to='static/img/',  # Directorio donde se guardarán las fotos dentro de MEDIA_ROOT
        null=True, 
        blank=True, 
        verbose_name='Imagen del Insumo'
    )

    class Meta:
        verbose_name = 'Insumo'
        verbose_name_plural = 'Insumos'
        ordering = ['cod_producto']
        
    def __str__(self):
        return f"{self.descripcion} ({self.cod_producto})"
