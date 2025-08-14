#!/usr/bin/env python
import os
import glob
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from booking.models import Booking

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix PDF linking issues by scanning and associating existing PDF files with bookings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making changes',
        )
        parser.add_argument(
            '--booking-id',
            type=int,
            help='Fix PDF for specific booking ID',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        specific_booking_id = options['booking_id']
        
        self.stdout.write(self.style.SUCCESS('Starting PDF link fix...'))
        
        # Get media directory
        media_root = settings.MEDIA_ROOT
        tickets_dir = os.path.join(media_root, 'tickets')
        
        if not os.path.exists(tickets_dir):
            self.stdout.write(self.style.ERROR(f'Tickets directory not found: {tickets_dir}'))
            return
        
        # Find all PDF files
        pdf_files = glob.glob(os.path.join(tickets_dir, '*.pdf'))
        self.stdout.write(f'Found {len(pdf_files)} PDF files')
        
        linked_count = 0
        missing_count = 0
        
        # Process bookings
        if specific_booking_id:
            bookings = Booking.objects.filter(id=specific_booking_id)
        else:
            bookings = Booking.objects.all()
        
        for booking in bookings:
            expected_filename = f"ticket_{booking.id}_{booking.train_number}_{booking.journey_date}.pdf"
            expected_path = os.path.join(tickets_dir, expected_filename)
            
            if os.path.exists(expected_path):
                # Update booking with PDF path
                if not dry_run:
                    booking.ticket_pdf = f"tickets/{expected_filename}"
                    booking.save(update_fields=['ticket_pdf'])
                    linked_count += 1
                else:
                    self.stdout.write(f'[DRY RUN] Would link {expected_filename} to booking {booking.id}')
            else:
                missing_count += 1
                self.stdout.write(f'[DRY RUN] Missing PDF: {expected_filename}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('This was a dry run - no changes were made'))
        else:
            self.stdout.write(self.style.SUCCESS(f'PDF link fix completed! Linked {linked_count} files, {missing_count} missing'))
