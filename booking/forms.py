from django import forms
from django.forms import inlineformset_factory
from .models import Booking, Passenger, Payment

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

class PaymentForm(forms.ModelForm):
    PAYMENT_METHODS = [
        ('UPI', 'UPI'),
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('NET_BANKING', 'Net Banking'),
        ('WALLET', 'Wallet'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHODS,
        widget=forms.RadioSelect(attrs={'class': 'payment-method'}),
        initial='UPI'
    )
    
    class Meta:
        model = Payment
        fields = ['payment_method', 'amount', 'upi_id', 'card_number', 
                 'card_holder_name', 'card_expiry', 'card_cvv', 'bank_name']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Amount',
                'min': '1',
                'step': '0.01'
            }),
            'upi_id': forms.TextInput(attrs={
                'class': 'form-control upi-field',
                'placeholder': 'UPI ID (e.g., name@upi)'
            }),
            'card_number': forms.TextInput(attrs={
                'class': 'form-control card-field',
                'placeholder': 'Card Number',
                'maxlength': '16'
            }),
            'card_holder_name': forms.TextInput(attrs={
                'class': 'form-control card-field',
                'placeholder': 'Card Holder Name'
            }),
            'card_expiry': forms.TextInput(attrs={
                'class': 'form-control card-field',
                'placeholder': 'MM/YY',
                'maxlength': '5'
            }),
            'card_cvv': forms.TextInput(attrs={
                'class': 'form-control card-field',
                'placeholder': 'CVV',
                'maxlength': '4'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control netbanking-field',
                'placeholder': 'Bank Name'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all payment detail fields not required initially
        for field in ['upi_id', 'card_number', 'card_holder_name', 
                     'card_expiry', 'card_cvv', 'bank_name']:
            self.fields[field].required = False

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
