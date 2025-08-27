from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Booking, Passenger, Payment
from .forms import BookingForm, PassengerFormSet, PaymentForm
from .tasks import execute_booking

@login_required
def dashboard(request):
    """Display all booking tasks for the logged-in user"""
    tasks = Booking.objects.filter(user=request.user).order_by('-booking_time')
    return render(request, 'booking/dashboard.html', {'tasks': tasks})

@login_required
def add_task(request):
    """Add a new booking task with passenger list and payment details"""
    if request.method == "POST":
        form = BookingForm(request.POST)
        passenger_formset = PassengerFormSet(request.POST, prefix='passengers')
        payment_form = PaymentForm(request.POST)
        
        if form.is_valid() and passenger_formset.is_valid() and payment_form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.status = "Scheduled"
            
            # Parse train name and number from train_name_number field
            train_info = booking.train_name_number
            if train_info and train_info != "Unknown Train 00000":
                parts = train_info.split()
                if len(parts) >= 2:
                    booking.train_number = parts[-1]
                    booking.train_name = ' '.join(parts[:-1])
                else:
                    booking.train_name = train_info
                    booking.train_number = "00000"
            else:
                booking.train_name = "Unknown Train"
                booking.train_number = "00000"
            
            booking.save()
            
            # Save payment details
            payment = payment_form.save(commit=False)
            payment.booking = booking
            payment.save()

            # Save passengers
            passengers = passenger_formset.save(commit=False)
            for passenger in passengers:
                passenger.booking = booking
                passenger.save()

            # Schedule execution at booking.booking_time if applicable
            if booking.booking_time and booking.booking_time > timezone.now() and payment.status == 'SUCCESS':
                execute_booking.apply_async(
                    args=[booking.id],
                    eta=booking.booking_time
                )
                print(f"[INFO] Booking {booking.id} scheduled for {booking.booking_time} with payment {payment.id}")
            else:
                execute_booking.delay(booking.id)
                print(f"[INFO] Booking {booking.id} executed immediately with payment {payment.id}")

            return redirect("dashboard")
    else:
        form = BookingForm()
        passenger_formset = PassengerFormSet(prefix='passengers')
        payment_form = PaymentForm()

    return render(request, "booking/add_task.html", {
        "form": form,
        "passenger_formset": passenger_formset,
        "payment_form": payment_form
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
