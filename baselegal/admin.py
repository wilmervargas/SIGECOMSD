from django.contrib import admin
from .models import BaselegalDB, BaselegalHistoricoDB  # Asegúrate de importar ambos modelos si quieres registrarlos en el admin

# Importa tus modelos
admin.site.register(BaselegalDB)
admin.site.register(BaselegalHistoricoDB)
