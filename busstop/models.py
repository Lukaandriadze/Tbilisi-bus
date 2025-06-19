from django.db import models

class BusStop(models.Model):
    arrival_time = models.CharField(max_length=255, null=True, blank=True)  # Arrival times for the buses
    stop_id = models.IntegerField(unique=True)  # Unique identifier for each bus stop
    name = models.CharField(max_length=255)     # Name of the bus stop
    def __str__(self):
        return f"Bus Stop {self.stop_id} - {self.name} - {self.arrival_time}"
