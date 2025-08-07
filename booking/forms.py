from django import forms
from .models import BookingTask

class BookingTaskForm(forms.ModelForm):
    class Meta:
        model = BookingTask
        exclude = ['user', 'status']
        widgets = {
            'journey_date': forms.DateInput(attrs={'type': 'date'}),
            'booking_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }