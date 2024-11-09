from django.contrib.auth.models import AbstractUser
from django.db import models

class UsuarioPersonalizado(AbstractUser):
    edad = models.PositiveIntegerField(null=True, blank=True)
    pais = models.CharField(max_length=100, null=True, blank=True)
    numero_telefono = models.CharField(max_length=15, null=True, blank=True)
    
    def __str__(self):
        return self.username

class Datos(models.Model):
    dia = models.DateField()
    clientes = models.IntegerField()

    def __str__(self):
        return f"{self.dia} - {self.clientes} clientes"
    
class HorarioMantencion(models.Model):
    dia_mantencion = models.CharField(max_length=10)  # Día de la semana
    horario_inicio = models.TimeField(default="08:00:00")
    horario_fin = models.TimeField(default="19:00:00")

    def __str__(self):
        return f'Mantención el {self.dia_mantencion}'
