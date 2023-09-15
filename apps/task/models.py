from uuid import uuid4

from django.db import models
from django.utils import timezone
from django.utils.timesince import timesince, timeuntil
from river.models import River
from userauth.models import CustomUser


class Task(models.Model):
    class Stage(models.TextChoices):
        # tasks are only available during these stages
        PLAN = "plan"
        ACT = "act"

    created_at = models.DateTimeField(default=timezone.now)
    uuid = models.UUIDField(default=uuid4, editable=False)
    name = models.CharField(max_length=120)
    river = models.ForeignKey(River, on_delete=models.CASCADE)
    stage_name = models.CharField(choices=Stage.choices, max_length=8)
    topic = models.CharField(max_length=32)
    done = models.BooleanField(default=False)
    due = models.DateTimeField(null=True, blank=True)
    responsible = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    @property
    def is_overdue(self):
        return self.due and self.due < timezone.now()

    @property
    def due_in(self) -> str:
        """If due, format as time until due, e.g. '6 days'"""
        if self.due and not self.is_overdue:
            return timeuntil(self.due, depth=1)
        return ""

    @property
    def overdue_by(self) -> str:
        """If overdue, format as time overdue, e.g. '2 weeks'"""
        if self.is_overdue:
            return timesince(self.due, depth=1)
        return ""
