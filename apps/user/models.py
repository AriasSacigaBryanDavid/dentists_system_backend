from django.contrib.auth.models import AbstractUser
from django.db import models
# IMPORTS
from apps.base.models import BaseModel

class User(AbstractUser, BaseModel):
    # We define the roles in the system
    class Role(models.TextChoices):
        ADMIN = '00', 'Admin'
        DOCTOR = '02', 'Doctor'
        RECEPTIONIST = '03', 'Recepcionista'

    # We define the Turn in the system
    class Turn(models.TextChoices):
        MORNING = 'morning', 'Mañana'
        AFTERNOON = 'afternoon', 'Tarde'

    role = models.CharField(max_length=2, choices=Role.choices, default=Role.RECEPTIONIST)
    turn = models.CharField(max_length=10, choices=Turn.choices, default=Turn.MORNING)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.user

    @property
    def full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.first_name.strip()

    def save(self, *args, **kwargs):
        # Synchronize the state (BaseModel) with `is_active` (Django)
        self.is_active = (self.status == self.RecordStatus.ACTIVE)
        super().save(*args, **kwargs)

