from django.apps import AppConfig


class ProtocolosConfig(AppConfig):
    # Se remueve default_auto_field ya que usas IDs enteros manuales en tus modelos principales
    name = 'protocolos'
    verbose_name = 'Gestión de Protocolos'  # Opcional: Cambia el nombre visual de esta app en el Django Admin