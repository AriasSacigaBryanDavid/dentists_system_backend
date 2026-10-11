from django.db import models
from django.conf import settings
from apps.base.models import BaseModel
from apps.customers.models import Customers

class Reservation(BaseModel):
    class State(models.IntegerChoices):
        PENDING = 1, 'Pendiente'
        CONFIRMED = 2, 'Confirmada'
        COMPLETED = 3, 'Completada'
        CANCELED = 4, 'Cancelada'

    customer = models.ForeignKey(
        Customers, 
        on_delete=models.CASCADE, 
        related_name='reservations'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='doctor_reservations'
    )
    date_time = models.DateTimeField()
    observation = models.TextField(blank=True, null=True)
    states = models.IntegerField(choices=State.choices, default=State.PENDING)

    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"

    def __str__(self):
        return f"Reserva de {self.customer} con Dr. {self.doctor} el {self.date_time.strftime('%Y-%m-%d %H:%M')}"
