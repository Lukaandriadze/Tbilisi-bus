# admin.py
from django.contrib import admin
from .models import BusStop

class BusStopAdmin(admin.ModelAdmin):
    list_display = ('arrival_time', 'stop_id') 
    search_fields = ('stop_id', 'arrival_time') 
    list_filter = ('arrival_time',)
admin.site.register(BusStop, BusStopAdmin)
