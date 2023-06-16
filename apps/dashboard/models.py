from django.db import models
from django.utils import timezone


class Wizard(models.Model):
    """
    Wizard is a singleton model. It only has one row, connected to the
    current SFS app instance.
    """

    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(blank=True, null=True)
