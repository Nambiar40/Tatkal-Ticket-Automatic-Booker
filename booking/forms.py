from django import forms
from django.forms import inlineformset_factory
from .models import Booking, Passenger

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "train_name_number",
            "source_station",
            "destination_station",
            "journey_date",
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

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['name', 'age', 'gender']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter passenger name'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Age',
                'min': '1',
                'max': '120'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            })
        }

# Create formset for passengers
PassengerFormSet = inlineformset_factory(
    Booking,
    Passenger,
    form=PassengerForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)
