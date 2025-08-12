import os
from django.conf import settings
from .models import Booking
from xhtml2pdf import pisa
from celery import shared_task

def html_to_pdf(source_html, output_filename):
    """Convert HTML string to PDF file."""
    with open(output_filename, "wb") as pdf_file:
        pisa.CreatePDF(source_html, dest=pdf_file)

def execute_booking():
    bookings = Booking.objects.all()

    for booking in bookings:
        ticket_html = f"""
        <html>
        <head><title>Train Ticket - {booking.train_number} - {booking.train_name}</title></head>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="border: 2px solid #000; padding: 20px; max-width: 600px;">
                <h1 style="text-align: center; color: #0066cc;">Train Ticket</h1>
                <hr>
                <p><strong>Booking ID:</strong> {booking.id}</p>
                <p><strong>Train:</strong> {booking.train_number} - {booking.train_name}</p>
                <p><strong>Passenger:</strong> {booking.passenger_name}</p>
                <p><strong>Age:</strong> {booking.passenger_age}</p>
                <p><strong>Gender:</strong> {booking.passenger_gender}</p>
                <p><strong>Date:</strong> {booking.date}</p>
                <p><strong>From:</strong> {booking.from_station}</p>
                <p><strong>To:</strong> {booking.to_station}</p>
                <p><strong>Class:</strong> {booking.travel_class}</p>
                <p><strong>Coach:</strong> {booking.coach}</p>
                <p><strong>Seat:</strong> {booking.seat}</p>
                <p><strong>PNR:</strong> {booking.pnr}</p>
                <hr>
                <p style="text-align: center; font-size: 12px; color: #666;">
                    Generated on {booking.generated_at.strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
        </body>
        </html>
        """

        # Save HTML file
        html_filename = f"ticket_{booking.id}_{booking.train_number} - {booking.train_name}_{booking.generated_at.strftime('%Y%m%d_%H%M%S')}.html"
        html_path = os.path.join(settings.MEDIA_ROOT, 'tickets', html_filename)
        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(ticket_html)

        # Save PDF file
        pdf_filename = html_filename.replace(".html", ".pdf")
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'tickets', pdf_filename)
        html_to_pdf(ticket_html, pdf_path)

        print(f"Saved ticket HTML: {html_path}")
        print(f"Saved ticket PDF: {pdf_path}")
