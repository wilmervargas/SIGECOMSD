from django.contrib import admin
from .models import ManualesDB, ManualesHistoricoDB  # Asegúrate de importar ambos modelos si quieres registrarlos en el admin


# Importa tus modelos
admin.site.register(ManualesDB)
admin.site.register(ManualesHistoricoDB)
