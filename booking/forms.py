from django import forms
from .models import BookingTask

class BookingTaskForm(forms.ModelForm):
    class Meta:
        model = BookingTask
        fields = [
            'train_name_number', 'source_station', 'destination_station', 
            'journey_date', 'passenger_name', 'passenger_age', 'passenger_gender', 
            'class_type', 'booking_time'
        ]
        widgets = {
            'journey_date': forms.DateInput(attrs={'type': 'date'}),
            'booking_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
