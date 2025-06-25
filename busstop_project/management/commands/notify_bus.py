# your_app/management/commands/notify_bus.py
from django.core.management.base import BaseCommand
from your_app.tasks import check_bus_arrival

class Command(BaseCommand):
    help = 'Starts the bus arrival check task'

    def handle(self, *args, **options):
        stop_id = 'your_stop_id'
        selected_short_name = 'your_bus_short_name'
        selected_time = 5  # example minutes
        user_email = 'user@example.com'

        check_bus_arrival.delay(stop_id, selected_short_name, selected_time, user_email)
        self.stdout.write(self.style.SUCCESS('Bus arrival checking task started!'))
