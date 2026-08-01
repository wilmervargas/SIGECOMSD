from django.apps import AppConfig


class FormulariosConfig(AppConfig):
    # Se remueve default_auto_field ya que usas IDs enteros manuales en tus modelos principales
    name = 'formularios'
    verbose_name = 'Gestión de Formularios'  # Opcional: Cambia el nombre visual de esta app en el Django Admin