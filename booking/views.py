from django.shortcuts import render, redirect
from .forms import BookingTaskForm
from .models import BookingTask
from django.contrib.auth.decorators import login_required
from .tasks import execute_booking
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from datetime import timedelta


@login_required
def dashboard(request):
    now = timezone.now()

    # ✅ Delete past bookings (before now)
    BookingTask.objects.filter(user=request.user, booking_time__lt=now).delete()

    # ✅ Delete completed bookings older than 1 hour
    BookingTask.objects.filter(
        user=request.user,
        status='completed',  # <-- Make sure your model has this field
        booking_time__lt=now - timedelta(hours=1)
    ).delete()

    # Fetch only upcoming + recently completed bookings
    tasks = BookingTask.objects.filter(user=request.user).order_by('booking_time')

    return render(request, 'booking/dashboard.html', {'tasks': tasks})


@login_required
def add_booking_task(request):
    if request.method == 'POST':
        form = BookingTaskForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            execute_booking.apply_async((booking.id,), eta=booking.booking_time)
            return redirect('dashboard')
    else:
        form = BookingTaskForm()
    return render(request, 'booking/add_task.html', {'form': form})


# ✅ New Signup View
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
