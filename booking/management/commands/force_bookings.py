from django.core.management.base import BaseCommand
from booking.models import BookingTask
from booking.tasks import execute_booking

class Command(BaseCommand):
    help = 'Force run all scheduled bookings immediately'

    def handle(self, *args, **kwargs):
        scheduled_tasks = BookingTask.objects.filter(status="Scheduled")
        for task in scheduled_tasks:
            execute_booking(task.id)
        self.stdout.write(self.style.SUCCESS(f'Forced {scheduled_tasks.count()} bookings.'))
