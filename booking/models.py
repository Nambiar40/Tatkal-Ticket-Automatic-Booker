from django.db import models
from django.contrib.auth.models import User

class Payment(models.Model):
    """Model to store payment details for bookings"""
    PAYMENT_METHODS = [
        ('UPI', 'UPI'),
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('NET_BANKING', 'Net Banking'),
        ('WALLET', 'Wallet'),
    ]
    
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    booking = models.OneToOneField('Booking', on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='UPI')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    upi_id = models.CharField(max_length=50, blank=True, null=True)
    card_number = models.CharField(max_length=16, blank=True, null=True)
    card_holder_name = models.CharField(max_length=100, blank=True, null=True)
    card_expiry = models.CharField(max_length=5, blank=True, null=True)
    card_cvv = models.CharField(max_length=4, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Payment for {self.booking.train_number} - {self.status}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Train details
    train_name_number = models.CharField(max_length=120, help_text="e.g., Rajdhani Express 12345", default="Unknown Train 00000")
    train_number = models.CharField(max_length=10, default="00000")
    train_name = models.CharField(max_length=100, default="Unknown Train")
    source_station = models.CharField(max_length=50, default="Unknown Source")
    destination_station = models.CharField(max_length=50, null=True, blank=True, default="Unknown Destination")

    journey_date = models.DateField(null=True, blank=True)

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
        return f"{self.train_number} - {self.user.username} ({self.journey_date})"

class Passenger(models.Model):
    booking = models.ForeignKey(Booking, related_name='passengers', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        default='Male'
    )
    seat_number = models.CharField(max_length=10, blank=True, null=True)
    coach_number = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.seat_number}"
