from django.db import models
from django.utils import timezone

from datetime import timedelta

class Session(models.Model):
    session_id = models.IntegerField()
    selected_timer = models.OneToOneField('Timer', on_delete=models.SET_NULL, null=True, blank=True)

class Timer(models.Model):
    duration = models.DurationField(default=timedelta)
    remaining = models.DurationField(default=timedelta) # Only used if timer is set to PAUSED, otherwise 0.
    end_at = models.DateTimeField(default=timezone.now)
    status = models.IntegerField(default=0)
    _session = models.ForeignKey(Session, on_delete=models.CASCADE)
