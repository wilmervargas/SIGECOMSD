from django.contrib import admin
from .models import EntradaEncabezado, EntradaDetalle


# Importa tus modelos
admin.site.register(EntradaEncabezado)
admin.site.register(EntradaDetalle)
