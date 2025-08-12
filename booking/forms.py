from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "train_name_number",
            "passenger_name",
            "passenger_age",
            "passenger_gender",
            "journey_date",
            "source_station",
            "destination_station",
            "class_type",
            "booking_time"
        ]
        widgets = {
            "booking_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "journey_date": forms.DateInput(attrs={"type": "date"})
        }

    def clean_booking_time(self):
        booking_time = self.cleaned_data["booking_time"]
        from django.utils import timezone
        if booking_time < timezone.now():
            raise forms.ValidationError("Booking time must be in the future.")
        return booking_time
