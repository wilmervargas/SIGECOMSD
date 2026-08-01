
from django.contrib import admin
from .models import SalidaEncabezado, SalidaDetalle

# Importa tus modelos
admin.site.register(SalidaEncabezado)
admin.site.register(SalidaDetalle)
