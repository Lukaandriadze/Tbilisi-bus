from django.core.management.base import BaseCommand
from buses.models import Buses  # Adjust the import if necessary
import requests

class Command(BaseCommand):
    help = 'Scrapes bus data and saves it to the database'

    def handle(self, *args, **kwargs):
        url = "https://transit.ttc.com.ge/pis-gateway/api/v3/routes?modes=BUS&locale=ka"
        headers = {
            "x-api-key": "c0a2f304-551a-4d08-b8df-2c53ecd57f9f",
            "accept": "application/json"
        }

        # Send the GET request to the API
        response = requests.get(url, headers=headers)
        bus_routes = response.json()

        # Loop through the routes and save them to the database
        for route in bus_routes:
            short_name = route.get('shortName')
            long_name = route.get('longName')
            route_id = route.get('id')
            
            # Save to the database if it's not already in there
            if not Buses.objects.filter(stop_id=route_id).exists():
                bus = Buses(
                    name=short_name,
                    stop_id=route_id,
                    BusNam=long_name
                )
                bus.save()
                self.stdout.write(self.style.SUCCESS(f"Successfully added {short_name} - {long_name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Bus {short_name} - {long_name} already exists"))

