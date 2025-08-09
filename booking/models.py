from django.db import models
from django.contrib.auth.models import User

class BookingTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Train details
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
    status = models.CharField(max_length=20, default="Scheduled")

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

    def __str__(self):
        return f"{self.train_number} - {self.passenger_name} ({self.journey_date})"
