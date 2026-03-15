from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking, Passenger, Payment
from .forms import BookingForm, PassengerFormSet, PaymentForm
from .tasks import execute_booking
import re

@login_required
def dashboard(request):
    """Display all booking tasks for the logged-in user"""
    tasks = Booking.objects.filter(user=request.user).order_by('-booking_time')
    return render(request, 'booking/dashboard.html', {'tasks': tasks})

@login_required
def add_task(request):
    """Add a new booking task with passenger list and payment details"""
    if request.method == "POST":
        # Manual parsing for hand-coded form - handles dynamic passengers
        booking_data = {
            'train_name_number': request.POST.get('train_name_number'),
            'source_station': request.POST.get('source_station'),
            'destination_station': request.POST.get('destination_station'),
            'journey_date': request.POST.get('journey_date'),
            'class_type': request.POST.get('class_type', 'SL'),
            'booking_time': request.POST.get('booking_time') or None,
        }
        
        if all([booking_data['train_name_number'], booking_data['source_station'], booking_data['destination_station'], booking_data['journey_date']]):
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                **{k: v for k, v in booking_data.items() if v},
                status="Scheduled"
            )
            
            # Parse train info
            train_info = booking.train_name_number
            parts = train_info.split()
            if len(parts) >= 2:
                booking.train_number = parts[-1]
                booking.train_name = ' '.join(parts[:-1])
            booking.save()
            
            # Passengers
            i = 0
            while request.POST.get(f'passengers-{i}-name'):
                name = request.POST.get(f'passengers-{i}-name')
                age = request.POST.get(f'passengers-{i}-age')
                gender = request.POST.get(f'passengers-{i}-gender')
                if name and age and gender:
                    Passenger.objects.create(
                        booking=booking,
                        name=name,
                        age=int(age),
                        gender=gender
                    )
                i += 1
            
            # Payment
            payment = Payment.objects.create(
                booking=booking,
                payment_method=request.POST.get('payment_method', 'UPI'),
                amount=float(request.POST.get('amount', 0)),
                status='PENDING',
                upi_id=request.POST.get('upi_id', ''),
                bank_name=request.POST.get('bank_name', ''),
                card_number=request.POST.get('card_number', '')
            )
            
            try:
                execute_booking.delay(booking.id)
            except:
                print("[WARNING] Celery Redis not running, booking saved but no async execution")
            
            messages.success(request, f'🚀 Booking #{booking.id} created! Check dashboard.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Fill all required booking fields.')
    
    else:
        form = BookingForm()
        passenger_formset = PassengerFormSet(prefix='passengers')
        payment_form = PaymentForm()

    return render(request, "booking/add_task.html", {
        "form": form,
        "passenger_formset": passenger_formset,
        "payment_form": payment_form,
        "messages": messages.get_messages(request)
    })

@login_required
def booking_details(request):
    """Step 1: Collect booking details"""
    if request.method == "POST":
        form = BookingForm(request.POST)
        passenger_formset = PassengerFormSet(request.POST, prefix='passengers')
        
        if form.is_valid() and passenger_formset.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.status = "Scheduled"
            booking.save()
            
            # Save passengers
            passengers = passenger_formset.save(commit=False)
            for passenger in passengers:
                passenger.booking = booking
                passenger.save()
            
            # Redirect to payment page with booking ID
            return redirect('payment', booking_id=booking.id)
    else:
        form = BookingForm()
        passenger_formset = PassengerFormSet(prefix='passengers')

    return render(request, "booking/booking_details.html", {
        "form": form,
        "passenger_formset": passenger_formset,
    })

@login_required
def payment(request, booking_id):
    """Step 2: Collect payment details"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Calculate fare
    fare = calculate_fare(booking)
    
    if request.method == "POST":
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            payment = payment_form.save(commit=False)
            payment.booking = booking
            payment.amount = fare
            payment.save()
            return redirect("dashboard")  # Redirect to dashboard after payment
    else:
        payment_form = PaymentForm(initial={'amount': fare})

    return render(request, "booking/payment.html", {
        "payment_form": payment_form,
        "booking": booking,
        "fare": fare,
    })

def calculate_fare(booking):
    """Calculate fare based on distance, class type, and number of passengers"""
    base_fare = 100  # Example base fare
    class_multiplier = {
        'SL': 1,
        '3A': 1.5,
        '2A': 2,
        '1A': 2.5
    }
    distance = 100  # Placeholder for distance calculation
    num_passengers = booking.passengers.count()
    
    fare = base_fare * class_multiplier.get(booking.class_type, 1) * num_passengers * (distance / 100)
    return round(fare, 2)

def autocomplete_stations(request):
    """Autocomplete for station names"""
    if 'term' in request.GET:
        term = request.GET.get('term')
        stations = [
            'Mumbai Central', 'Mumbai CST', 'Bandra Terminus', 
            'Delhi Junction', 'New Delhi', 'Hazrat Nizamuddin',
            'Kolkata Howrah', 'Kolkata Sealdah', 'Kolkata Shalimar',
            'Chennai Central', 'Chennai Egmore', 'Bangalore City',
            'Pune Junction', 'Ahmedabad Junction', 'Jaipur Junction'
        ]
        filtered_stations = [s for s in stations if term.lower() in s.lower()]
        return JsonResponse(filtered_stations[:10], safe=False)
    return JsonResponse([], safe=False)

def autocomplete_trains(request):
    """Autocomplete for train names and numbers"""
    if 'term' in request.GET:
        term = request.GET.get('term')
        trains = [
            'Rajdhani Express 12345', 'Shatabdi Express 12001', 
            'Duronto Express 12221', 'Garib Rath 12111',
            'Jan Shatabdi 12051', 'Intercity Express 11015',
            'Superfast Express 12137', 'Mail Express 11033',
            'Passenger 56003', 'Express 12625'
        ]
        filtered_trains = [t for t in trains if term.lower() in t.lower()]
        return JsonResponse(filtered_trains[:10], safe=False)
    return JsonResponse([], safe=False)

def create_booking(request):
    """Legacy create booking view - redirects to add_task"""
    return redirect('add_task')

@login_required
def task_detail(request, task_id):
    """Display detailed information about a specific booking task."""
    from django.shortcuts import get_object_or_404
    
    task = get_object_or_404(Booking, id=task_id, user=request.user)
    passengers = task.passengers.all()
    return render(request, 'booking/task_detail.html', {
        'task': task,
        'passengers': passengers
    })
