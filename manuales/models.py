
from django.db import models
from django.utils import timezone
from dependencias.models import DependenciasBD

# =========================================================
# MODELO PRINCIPAL: MANUALES
# =========================================================
class ManualesDB(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')

    # IMPORTANTE: Cambiado default a False para que no rompa la regla al crear registros en masa por accidente
    vigente = models.BooleanField(default=False, verbose_name='Vigente')
    
    cod_manual = models.CharField(max_length=20, verbose_name='Código Manual')
    titulo = models.TextField(verbose_name='Título actual')
    
    fecha_elaboracion = models.DateField(blank=True, null=True, default=timezone.now, verbose_name='Fecha de elaboración')
    fecha_revision = models.DateField(blank=True, null=True, default=timezone.now, verbose_name='Fecha de revisión')
    fecha_aprobacion = models.DateField(blank=True, null=True, default=timezone.now, verbose_name='Fecha de aprobación')
    
    version = models.CharField(blank=True, null=True, max_length=20, verbose_name='Versión actual')
    distribucion_digital = models.BooleanField(default=True, verbose_name='Dist. digital')
    distribucion_fisica = models.BooleanField(default=False, verbose_name='Dist. física')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    cod_dependencia = models.ForeignKey(
        'dependencias.DependenciasBD',  
        on_delete=models.PROTECT,  # Se cambia a PROTECT porque ya no puede ser NULL si se borra una dependencia
        default=1,                 # <--- Reemplaza el 1 por el ID de tu dependencia comodín
        verbose_name='Dependencia',
        related_name='manuales'
    )

    # NUEVO CAMPO: Archivo PDF del manual actual
    archivo_pdf = models.FileField(
        blank=True, 
        null=True, 
        verbose_name='Ejemplar PDF Actual'
    )

    class Meta:
        verbose_name = 'Manual'
        verbose_name_plural = 'Manuales'
        ordering = ['cod_dependencia', 'id']
        
    def __str__(self):
        return f"Cod.Manual {self.cod_manual}"


# =========================================================
# MODELO: HISTÓRICO DE MANUALES (ADAPTADO)
# =========================================================
class ManualesHistoricoDB(models.Model):
    manual = models.ForeignKey(
        ManualesDB,
        on_delete=models.PROTECT,  # Se cambia a PROTECT para preservar el histórico aunque se borre el manual
        related_name='historicos',
        verbose_name='Manual'
    )
    
    cod_manual = models.CharField(blank=True, null=True, max_length=20, verbose_name='Código Manual')
    titulo = models.TextField(blank=True, null=True, verbose_name='Título anterior')
    
    fecha_elaboracion = models.DateField(blank=True, null=True, default=timezone.now, verbose_name='Fecha de elaboración')
    fecha_revision = models.DateField(blank=True, null=True, default=timezone.now, verbose_name='Fecha de revisión')
    fecha_aprobacion = models.DateField(blank=True, null=True, default=timezone.now, verbose_name='Fecha de aprobación')
    
    version = models.CharField(blank=True, null=True, max_length=20, verbose_name='Versión anterior')
    distribucion_digital = models.BooleanField(default=True, verbose_name='Dist. digital')
    distribucion_fisica = models.BooleanField(default=False, verbose_name='Dist. física')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    # NUEVO CAMPO: Archivo PDF del manual actual
    archivo_pdf = models.FileField(
        blank=True, 
        null=True, 
        verbose_name='Ejemplar PDF Actual'
    )

    class Meta:
        verbose_name = 'Historial de Manual'
        verbose_name_plural = 'Historial de Manuales'
        ordering = ['-fecha_aprobacion', 'manual']
        
    def __str__(self):
        return f"Histórico Manual {self.manual_id} - Ver: {self.version or 'S/V'}"