from django.contrib import admin
from .models import ProtocolosDB, ProtocolosHistoricoDB  # Asegúrate de importar ambos modelos si quieres registrarlos en el admin


# Importa tus modelos
admin.site.register(ProtocolosDB)
admin.site.register(ProtocolosHistoricoDB)
