from django.apps import AppConfig


class ProcedimientosConfig(AppConfig):
    # Se remueve default_auto_field ya que usas IDs enteros manuales en tus modelos principales
    name = 'procedimientos'
    verbose_name = 'Gestión de Procedimientos'  # Opcional: Cambia el nombre visual de esta app en el Django Admin