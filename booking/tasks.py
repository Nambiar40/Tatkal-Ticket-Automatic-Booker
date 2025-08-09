from celery import shared_task
from .models import BookingTask
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import random
import os
from django.conf import settings

@shared_task
def execute_booking(task_id):
    try:
        booking = BookingTask.objects.get(id=task_id)

        # Simulate booking process
        booking.status = "Completed"
        
        # Generate mock PNR and seat details
        booking.pnr_number = str(random.randint(1000000000, 9999999999))
        booking.seat_number = f"S{random.randint(1, 12)}-{random.randint(1, 80)}"
        booking.coach_number = f"C{random.randint(1, 18)}"
        booking.save()

        # Generate PDF ticket
        pdf_filename = f"ticket_{booking.id}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, "tickets", pdf_filename)
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        c = canvas.Canvas(pdf_path, pagesize=A4)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(200, 800, "Tatkal Auto Booker - E-Ticket")

        c.setFont("Helvetica", 14)
        c.drawString(100, 750, f"PNR Number: {booking.pnr_number}")
        c.drawString(100, 720, f"Train: {booking.train_number} - {booking.train_name}")
        c.drawString(100, 690, f"From: {booking.source_station} To: {booking.destination_station}")
        c.drawString(100, 660, f"Journey Date: {booking.journey_date.strftime('%Y-%m-%d')}")
        c.drawString(100, 630, f"Passenger: {booking.passenger_name} ({booking.passenger_gender}, {booking.passenger_age} yrs)")
        c.drawString(100, 600, f"Class: {booking.class_type}, Coach: {booking.coach_number}, Seat: {booking.seat_number}")

        c.showPage()
        c.save()

        booking.ticket_pdf = f"tickets/{pdf_filename}"
        booking.save()

        print(f"[TEST] Booking for task ID {task_id} completed successfully. Ticket saved at {pdf_path}")

    except BookingTask.DoesNotExist:
        print(f"[ERROR] Booking task {task_id} not found.")
