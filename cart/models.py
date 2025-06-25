from django.db import models
from django.conf import settings
from buses.models import Buses
from busstop.models import BusStop


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bus_stop = models.ForeignKey(BusStop, on_delete=models.CASCADE)
    bus = models.ForeignKey(Buses, on_delete=models.CASCADE, null=True, blank=True)
    selected_time = models.IntegerField()
    short_name = models.CharField(max_length=20, null=True, blank=True)
    notified = models.BooleanField(default=False)  # <-- ეს დაამატე

    def __str__(self):
        bus_name = self.bus.name if self.bus else "უცნობი"
        return f"{self.user} - {bus_name} - {self.bus_stop.name} @ {self.selected_time} წთ"
