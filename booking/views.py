from django.shortcuts import render, redirect
from .forms import BookingTaskForm
from .models import BookingTask
from django.contrib.auth.decorators import login_required
from .tasks import execute_booking
from django.contrib.auth.forms import UserCreationForm 
from celery import shared_task 
from django.utils import timezone
from datetime import timedelta


@login_required
def dashboard(request):
    tasks = BookingTask.objects.filter(user=request.user)
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
@shared_task

@shared_task
def delete_old_tasks():
    cutoff = timezone.now() - timedelta(days=1)  # Older than 1 day
    deleted_count, _ = BookingTask.objects.filter(booking_time__lt=cutoff).delete()
    print(f"Deleted {deleted_count} old booking tasks")

