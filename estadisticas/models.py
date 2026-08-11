# estadisticas/models.py
from django.db import models

class Ranking(models.Model):
    class Meta:
        managed = False  # <--- ¡IMPORTANTE! Django NO creará una tabla en la base de datos
        default_permissions = ()  # Evita que genere add, change, delete o view por defecto
        permissions = [
            ("view_ranking", "Puede ver el ranking de salidas"),  # Tu permiso personalizado
        ]