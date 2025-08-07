from django.shortcuts import render, redirect
from .forms import BookingTaskForm
from .models import BookingTask
from django.contrib.auth.decorators import login_required
from .tasks import execute_booking

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