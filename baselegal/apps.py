from django.apps import AppConfig

class BaselegalConfig(AppConfig):
    # Se remueve default_auto_field ya que usas IDs enteros manuales en tus modelos principales
    name = 'baselegal'
    verbose_name = 'Gestión de Base Legal'  # Opcional: Cambia el nombre visual de esta app en el Django Admin