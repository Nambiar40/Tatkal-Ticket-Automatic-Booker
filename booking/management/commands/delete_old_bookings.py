from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from booking.models import Booking
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Manually delete old completed bookings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Delete bookings older than this many days (default: 1)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion regardless of retention settings'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS(f"Starting deletion of bookings older than {days} day(s)")
        )
        
        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Get bookings to delete
        if force:
            bookings = Booking.objects.filter(
                status='Completed',
                booking_time__lt=cutoff_date
            )
        else:
            bookings = Booking.objects.filter(
                status='Completed',
                auto_delete_enabled=True,
                booking_time__lt=cutoff_date
            )
        
        count = bookings.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN: Would delete {count} bookings")
            )
            for booking in bookings:
                self.stdout.write(
                    f"  - {booking.id}: {booking.train_name_number} ({booking.booking_time})"
                )
        else:
            deleted_count = 0
            for booking in bookings:
                try:
                    booking.delete_with_files()
                    deleted_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Deleted booking {booking.id}")
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error deleting booking {booking.id}: {e}")
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f"Successfully deleted {deleted_count} bookings")
            )
