from django.apps import AppConfig


class ManualesConfig(AppConfig):
    # Se remueve default_auto_field ya que usas IDs enteros manuales en tus modelos principales
    name = 'manuales'
    verbose_name = 'Gestión de Manuales'  # Opcional: Cambia el nombre visual de esta app en el Django Admin