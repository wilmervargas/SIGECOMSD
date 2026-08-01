from django.contrib import admin
from .models import FormulariosDB, FormulariosHistoricoDB  # Asegúrate de importar ambos modelos si quieres registrarlos en el admin


# Importa tus modelos
admin.site.register(FormulariosDB)
admin.site.register(FormulariosHistoricoDB)
