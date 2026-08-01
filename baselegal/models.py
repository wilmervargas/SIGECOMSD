
from django.db import models
from django.utils import timezone

# =========================================================
# MODELO PRINCIPAL: Baselegal
# =========================================================
class BaselegalDB(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')

    # IMPORTANTE: Cambiado default a False para que no rompa la regla al crear registros en masa por accidente
    vigente = models.BooleanField(default=False, verbose_name='Vigente')
    
    cod_baselegal = models.CharField(max_length=20, verbose_name='Código Base Legal')
    titulo = models.TextField(verbose_name='Título actual')
    fecha_aprobacion = models.DateField(blank=True, null=True, default=timezone.now, verbose_name='Fecha de aprobación')

    nro_gaceta = models.CharField(blank=True, null=True, max_length=20, verbose_name='Número de Gaceta')
    fecha_publicacion = models.DateField(blank=True, null=True, default=timezone.now, verbose_name='Fecha de publicación')
    # 1. Definimos las opciones dentro del modelo (pueden ser tuplas o una clase TextChoices)
    class TipoPublicacion(models.TextChoices):
        ORDINARIA = 'ORD', 'Ordinaria'
        EXTRAORDINARIA = 'EXT', 'Extraordinaria'
        OTRA = 'OTR', 'Otra'

    # 2. Reemplazamos el ForeignKey por el CharField con choices
    tipo = models.CharField(
        max_length=3,
        choices=TipoPublicacion.choices,
        default=TipoPublicacion.ORDINARIA,
        verbose_name='Tipo de Publicación / Gaceta',
        help_text='Seleccione si la publicación es Ordinaria, Extraordinaria u Otra'
    )
    # 1. Definimos las opciones dentro del modelo (pueden ser tuplas o una clase TextChoices)
    class OrganoPublica(models.TextChoices):
        MUNICIPAL = 'MUN', 'Gaceta Municipal'
        REGIONAL = 'REG', 'Gaceta Oficial del Estado Carabobo'
        NACIONAL = 'NAC', 'Gaceta Oficial de la República Bolivariana de Venezuela'
        OTRA = 'OTR', 'Otra'

    # 2. Reemplazamos el ForeignKey por el CharField con choices
    organo_publica = models.CharField(
        max_length=3,
        choices=OrganoPublica.choices,
        default=OrganoPublica.MUNICIPAL,
        verbose_name='Organo que publica',
        help_text='Seleccione Organo que publica'
    )

    distribucion_digital = models.BooleanField(default=True, verbose_name='Dist. digital')
    distribucion_fisica = models.BooleanField(default=False, verbose_name='Dist. física')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    # NUEVO CAMPO: Archivo PDF del baselegal actual
    archivo_pdf = models.FileField(
        blank=True, 
        null=True, 
        verbose_name='Ejemplar PDF Actual'
    )

    class Meta:
        verbose_name = 'Base Legal'
        verbose_name_plural = 'Baselegal'
        ordering = ['id']
        
    def __str__(self):
        return f"Num. Base Legal {self.cod_baselegal}"


# =========================================================
# MODELO: HISTÓRICO DE Baselegal (ADAPTADO)
# =========================================================
class BaselegalHistoricoDB(models.Model):
    baselegal = models.ForeignKey(
        BaselegalDB,
        on_delete=models.PROTECT,
        related_name='historicos',
        verbose_name='Base Legal'
    )
    
    cod_baselegal = models.CharField(blank=True, null=True, max_length=20, verbose_name='Código Base Legal')
    titulo = models.TextField(blank=True, null=True, verbose_name='Título anterior')
    fecha_aprobacion = models.DateField(blank=True, null=True, default=timezone.now, verbose_name='Fecha de aprobación')

    nro_gaceta = models.CharField(blank=True, null=True, max_length=20, verbose_name='Número de Gaceta')
    fecha_publicacion = models.DateField(blank=True, null=True, default=timezone.now, verbose_name='Fecha de publicación')
    # 1. Definimos las opciones dentro del modelo (pueden ser tuplas o una clase TextChoices)
    class TipoPublicacion(models.TextChoices):
        ORDINARIA = 'ORD', 'Ordinaria'
        EXTRAORDINARIA = 'EXT', 'Extraordinaria'
        OTRA = 'OTR', 'Otra'

    # 2. Reemplazamos el ForeignKey por el CharField con choices
    tipo = models.CharField(
        max_length=3,
        choices=TipoPublicacion.choices,
        default=TipoPublicacion.ORDINARIA,
        verbose_name='Tipo de Publicación / Gaceta',
        help_text='Seleccione si la publicación es Ordinaria, Extraordinaria u Otra'
    )
    # 1. Definimos las opciones dentro del modelo (pueden ser tuplas o una clase TextChoices)
    class OrganoPublica(models.TextChoices):
        MUNICIPAL = 'MUN', 'Gaceta Municipal'
        REGIONAL = 'REG', 'Gaceta Oficial del Estado Carabobo'
        NACIONAL = 'NAC', 'Gaceta Oficial de la República Bolivariana de Venezuela'
        OTRA = 'OTR', 'Otra'

    # 2. Reemplazamos el ForeignKey por el CharField con choices
    organo_publica = models.CharField(
        max_length=3,
        choices=OrganoPublica.choices,
        default=OrganoPublica.MUNICIPAL,
        verbose_name='Organo que publica',
        help_text='Seleccione Organo que publica'
    )

    distribucion_digital = models.BooleanField(default=True, verbose_name='Dist. digital')
    distribucion_fisica = models.BooleanField(default=False, verbose_name='Dist. física')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    # NUEVO CAMPO: Archivo PDF del baselegal actual
    archivo_pdf = models.FileField(
        blank=True, 
        null=True, 
        verbose_name='Ejemplar PDF Actual'
    )

    class Meta:
        verbose_name = 'Historial de Base Legal'
        verbose_name_plural = 'Historial de Baselegal'
        ordering = ['-fecha_aprobacion', 'baselegal']
        
    def __str__(self):
        return f"Histórico Base Legal {self.baselegal_id} - Aprobado el {self.fecha_aprobacion}"