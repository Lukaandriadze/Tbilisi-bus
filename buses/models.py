from django.db import models

class Buses(models.Model):
    name = models.CharField(max_length=100)
    stop_id = models.CharField(max_length=255, unique=True)  
    BusNam = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.BusNam}- {self.stop_id}"
