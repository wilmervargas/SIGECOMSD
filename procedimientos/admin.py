from django.contrib import admin
from .models import ProcedimientosDB, ProcedimientosHistoricoDB  # Asegúrate de importar ambos modelos si quieres registrarlos en el admin


# Importa tus modelos
admin.site.register(ProcedimientosDB)
admin.site.register(ProcedimientosHistoricoDB)
