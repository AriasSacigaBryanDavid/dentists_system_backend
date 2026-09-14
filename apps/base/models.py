from uuid import UUID
from django.db import models
from django.conf import settings
import uuid


class BaseModel(models.Model):

    class RecordStatus(models.IntegerChoices):
        DELETED = 0, 'Deleted'
        ACTIVE = 1, 'Active'

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_%(class)s_set')
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='updated_%(class)s_set'
    )
    status = models.PositiveSmallIntegerField(
        choices=RecordStatus.choices,
        default=RecordStatus.ACTIVE
    )

    class Meta:
        abstract = True

