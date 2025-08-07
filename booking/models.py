from django.db import models
from django.contrib.auth.models import User

class BookingTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    train_number = models.CharField(max_length=10)
    journey_date = models.DateField()
    booking_time = models.DateTimeField()
    passenger_name = models.CharField(max_length=100)
    passenger_age = models.IntegerField()
    class_type = models.CharField(max_length=10)
    status = models.CharField(max_length=20, default='Scheduled')

    def __str__(self):
        return f"{self.user.username} → {self.train_number} on {self.journey_date}"