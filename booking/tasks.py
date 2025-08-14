import os
import logging
from celery import shared_task
from django.conf import settings
from .models import Booking
from xhtml2pdf import pisa
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def html_to_pdf(source_html, output_filename):
    """Convert HTML string to PDF file."""
    with open(output_filename, "wb") as pdf_file:
        pisa.CreatePDF(source_html, dest=pdf_file)

@shared_task
def execute_booking(booking_id=None):
    """Execute booking and update status to completed"""
    logger.info(f"Starting execute_booking for booking_id: {booking_id}")
    
    # Get specific booking or all bookings
    if booking_id:
        bookings = Booking.objects.filter(id=booking_id)
    else:
        bookings = Booking.objects.all()

    for booking in bookings:
        try:
            logger.info(f"Processing booking {booking.id} - current status: {booking.status}")
            
            # Skip if already completed
            if booking.status == "Completed":
                logger.info(f"Booking {booking.id} already completed, skipping")
                continue
                
            # Simulate booking completion with mock PNR, seat, and coach numbers
            import random
            import string
            
            # Generate mock PNR (10-digit alphanumeric)
            pnr = ''.join(random.choices(string.digits, k=10))
            booking.pnr_number = pnr
            
            # Generate mock coach and seat based on class
            coach_prefix = {
                'SL': 'S',
                '3A': 'B',
                '2A': 'A',
                '1A': 'H'
            }.get(booking.class_type, 'C')
            
            # Get all passengers for this booking
            passengers = booking.passengers.all()
            
            # Assign individual seat numbers to each passenger
            if booking.class_type == 'SL':
                seat_range = (1, 72)
            elif booking.class_type == '3A':
                seat_range = (1, 64)
            elif booking.class_type == '2A':
                seat_range = (1, 46)
            elif booking.class_type == '1A':
                seat_range = (1, 24)
            else:
                seat_range = (1, 50)
            
            # Generate unique seat numbers for each passenger
            available_seats = list(range(seat_range[0], seat_range[1] + 1))
            random.shuffle(available_seats)
            
            # Assign coach and seat to each passenger
            coach_number = f"{coach_prefix}{random.randint(1, 12)}"
            for i, passenger in enumerate(passengers):
                passenger.coach_number = coach_number
                passenger.seat_number = str(available_seats[i] if i < len(available_seats) else random.randint(*seat_range))
                passenger.save()
            
            # Keep the booking-level coach number for backward compatibility
            booking.coach_number = coach_number
            booking.seat_number = str(available_seats[0]) if passengers else str(random.randint(*seat_range))
            
            # Update booking status
            booking.status = "Completed"
            booking.save(update_fields=['status', 'pnr_number', 'coach_number', 'seat_number'])
            logger.info(f"Booking {booking.id} status updated to Completed")
            
            # Generate passenger details for ticket
            passenger_info = []
            for passenger in passengers:
                passenger_info.append(f"{passenger.name} ({passenger.age}, {passenger.gender}) - Seat: {passenger.seat_number}")
            
            passenger_details = "<br>".join(passenger_info) if passenger_info else "No passenger details available"

            ticket_html = f"""
            <html>
            <head><title>Train Ticket - {booking.train_number} - {booking.train_name}</title></head>
            <body style="font-family: Arial, sans-serif; margin: 20px;">
                <div style="border: 2px solid #000; padding: 20px; max-width: 600px;">
                    <h1 style="text-align: center; color: #0066cc;">Train Ticket</h1>
                    <hr>
                    <p><strong>Booking ID:</strong> {booking.id}</p>
                    <p><strong>Train:</strong> {booking.train_number} - {booking.train_name}</p>
                    <p><strong>Passengers:</strong><br>{passenger_details}</p>
                    <p><strong>Journey Date:</strong> {booking.journey_date}</p>
                    <p><strong>From:</strong> {booking.source_station}</p>
                    <p><strong>To:</strong> {booking.destination_station}</p>
                    <p><strong>Class:</strong> {booking.class_type}</p>
                    <p><strong>Coach:</strong> {booking.coach_number}</p>
                    <p><strong>Seat:</strong> {booking.seat_number}</p>
                    <p><strong>PNR:</strong> {booking.pnr_number}</p>
                    <hr>
                    <p style="text-align: center; color: #0066cc; font-size: 12px;">
                        This is a simulated booking for demonstration purposes
                    </p>
                </div>
            </body>
            </html>
            """

            # Save HTML file
            html_filename = f"ticket_{booking.id}_{booking.train_number}_{booking.journey_date}.html"
            html_path = os.path.join(settings.MEDIA_ROOT, 'tickets', html_filename)
            os.makedirs(os.path.dirname(html_path), exist_ok=True)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(ticket_html)

            # Save PDF file
            pdf_filename = html_filename.replace(".html", ".pdf")
            pdf_path = os.path.join(settings.MEDIA_ROOT, 'tickets', pdf_filename)
            html_to_pdf(ticket_html, pdf_path)

            # Save PDF path to booking
            booking.ticket_pdf = f"tickets/{pdf_filename}"
            booking.save(update_fields=['ticket_pdf'])
            
            logger.info(f"Successfully processed booking {booking.id}")
            print(f"Saved ticket HTML: {html_path}")
            print(f"Saved ticket PDF: {pdf_path}")
            print(f"Generated mock booking: PNR={booking.pnr_number}, Coach={booking.coach_number}, Seat={booking.seat_number}")

        except Exception as e:
            logger.error(f"Error processing booking {booking.id}: {str(e)}")
            booking.status = "Failed"
            booking.save(update_fields=['status'])
            raise e

@shared_task
def update_scheduled_bookings():
    """Update and process scheduled bookings that are ready for execution."""
    from datetime import datetime
    
    # Get bookings that are scheduled and ready to process
    scheduled_bookings = Booking.objects.filter(
        status='Scheduled',
        journey_date__gte=datetime.now().date()
    )
    
    for booking in scheduled_bookings:
        # Check if booking should be processed now
        if booking.journey_date == datetime.now().date():
            logger.info(f"Processing scheduled booking: {booking.id}")
            # Trigger the booking execution
            execute_booking.delay(booking.id)
            booking.status = 'processing'
            booking.save(update_fields=['status'])
    
    logger.info(f"Updated {scheduled_bookings.count()} scheduled bookings")
    return f"Processed {scheduled_bookings.count()} scheduled bookings"

@shared_task
def auto_delete_old_bookings():
    """Automatically delete old completed bookings based on retention policy."""
    from django.utils import timezone
    
    logger.info("Starting auto-deletion of old completed bookings")
    
    # Get all completed bookings that are eligible for deletion
    completed_bookings = Booking.objects.filter(status='Completed')
    
    deleted_count = 0
    skipped_count = 0
    
    for booking in completed_bookings:
        if booking.is_deletable():
            try:
                logger.info(f"Deleting booking {booking.id} - {booking.train_name_number}")
                booking.delete_with_files()
                deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting booking {booking.id}: {str(e)}")
                skipped_count += 1
        else:
            skipped_count += 1
    
    logger.info(f"Auto-deletion completed: {deleted_count} deleted, {skipped_count} skipped")
    return f"Auto-deleted {deleted_count} old bookings, skipped {skipped_count}"

@shared_task
def cleanup_orphaned_files():
    """Clean up orphaned ticket files that don't have corresponding bookings."""
    import os
    import glob
    
    logger.info("Starting cleanup of orphaned ticket files")
    
    # Get all ticket files in the media directory
    ticket_dir = os.path.join(settings.MEDIA_ROOT, 'tickets')
    if not os.path.exists(ticket_dir):
        logger.info("Ticket directory does not exist")
        return
    
    # Get all existing booking PDFs
    existing_pdfs = set()
    for booking in Booking.objects.filter(ticket_pdf__isnull=False):
        if booking.ticket_pdf:
            existing_pdfs.add(str(booking.ticket_pdf))
    
    # Find all PDF files in the tickets directory
    orphaned_files = []
    for file_path in glob.glob(os.path.join(ticket_dir, "*.pdf")):
        relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
        if relative_path not in existing_pdfs:
            orphaned_files.append(file_path)
    
    # Delete orphaned files
    deleted_files = 0
    for file_path in orphaned_files:
        try:
            os.remove(file_path)
            logger.info(f"Deleted orphaned file: {file_path}")
            deleted_files += 1
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
    
    # Also clean up HTML files
    orphaned_html_files = []
    for file_path in glob.glob(os.path.join(ticket_dir, "*.html")):
        # Check if corresponding PDF exists
        pdf_path = file_path.replace(".html", ".pdf")
        if not os.path.exists(pdf_path):
            orphaned_html_files.append(file_path)
    
    for file_path in orphaned_html_files:
        try:
            os.remove(file_path)
            logger.info(f"Deleted orphaned HTML file: {file_path}")
            deleted_files += 1
        except Exception as e:
            logger.error(f"Error deleting HTML file {file_path}: {str(e)}")
    
    logger.info(f"Cleanup completed: {deleted_files} orphaned files deleted")
    return f"Cleaned up {deleted_files} orphaned files"
