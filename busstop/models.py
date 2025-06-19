from django.db import models
from django.contrib.auth.models import User

class BusStop(models.Model):
    stop_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    bus_number = models.CharField(max_length=20)  # ავტობუსის ნომერი
    arrival_time = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.bus_number})"

