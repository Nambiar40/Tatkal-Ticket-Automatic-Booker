from django.db import models
from django.contrib.auth.models import User

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Train details
    train_name_number = models.CharField(max_length=120, help_text="e.g., Rajdhani Express 12345", default="Unknown Train 00000")
    train_number = models.CharField(max_length=10, default="00000")
    train_name = models.CharField(max_length=100, default="Unknown Train")
    source_station = models.CharField(max_length=50, default="Unknown Source")
    destination_station = models.CharField(max_length=50, null=True, blank=True, default="Unknown Destination")

    journey_date = models.DateField(null=True, blank=True)

    # Passenger details
    passenger_name = models.CharField(max_length=100, default="Test Passenger")
    passenger_age = models.PositiveIntegerField(default=0)
    passenger_gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        default='Male'
    )

    # Booking info
    booking_time = models.DateTimeField(null=True, blank=True)
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')

    # Ticket info (auto-filled after booking)
    pnr_number = models.CharField(max_length=12, blank=True, null=True)
    seat_number = models.CharField(max_length=10, blank=True, null=True)
    coach_number = models.CharField(max_length=5, blank=True, null=True)
    class_type = models.CharField(
        max_length=20,
        choices=[
            ('SL', 'Sleeper'),
            ('3A', '3rd AC'),
            ('2A', '2nd AC'),
            ('1A', '1st AC')
        ],
        default='SL'
    )

    # Ticket PDF
    ticket_pdf = models.FileField(upload_to="tickets/", blank=True, null=True)
    ticket_pdf_url = models.URLField(blank=True, null=True)
    
    # Auto-deletion fields
    auto_delete_enabled = models.BooleanField(default=True)
    retention_days = models.PositiveIntegerField(default=30)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.train_number} - {self.passenger_name} ({self.journey_date})"
    
    def is_deletable(self):
        """Check if this booking can be auto-deleted"""
        if not self.auto_delete_enabled:
            return False
        
        if self.status != "Completed":
            return False
            
        if not self.booking_time:
            return False
            
        from django.utils import timezone
        from datetime import timedelta
        
        retention_date = self.booking_time + timedelta(days=self.retention_days)
        return timezone.now() >= retention_date
    
    def delete_with_files(self):
        """Delete booking and associated files"""
        if self.ticket_pdf:
            try:
                import os
                from django.conf import settings
                file_path = os.path.join(settings.MEDIA_ROOT, str(self.ticket_pdf))
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {self.ticket_pdf}: {e}")
        
        self.delete()
