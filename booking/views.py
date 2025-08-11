from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import BookingTask
from .forms import BookingTaskForm

# Sample data for autocomplete
INDIAN_STATIONS = [
    "Mumbai Central", "Mumbai CST", "Mumbai Bandra", "Mumbai Dadar",
    "Delhi Junction", "New Delhi", "Delhi Cantt", "Delhi Sarai Rohilla",
    "Kolkata Howrah", "Kolkata Sealdah", "Kolkata Shalimar",
    "Chennai Central", "Chennai Egmore", "Chennai Beach",
    "Bangalore City", "Bangalore Cantt", "Bangalore East",
    "Hyderabad Deccan", "Hyderabad Lingampally", "Secunderabad",
    "Ahmedabad Junction", "Pune Junction", "Jaipur Junction",
    "Lucknow Charbagh", "Patna Junction", "Bhopal Junction",
    "Thiruvananthapuram Central", "Kochi Ernakulam", "Guwahati"
]

INDIAN_TRAINS = [
    {"number": "12001", "name": "Habibganj New Delhi Shatabdi Express"},
    {"number": "12002", "name": "New Delhi Habibganj Shatabdi Express"},
    {"number": "12137", "name": "Punjab Mail"},
    {"number": "12138", "name": "Punjab Mail"},
    {"number": "12221", "name": "Pune Howrah Duronto Express"},
    {"number": "12222", "name": "Howrah Pune Duronto Express"},
    {"number": "12301", "name": "Howrah New Delhi Rajdhani Express"},
    {"number": "12302", "name": "New Delhi Howrah Rajdhani Express"},
    {"number": "12621", "name": "Tamil Nadu Express"},
    {"number": "12622", "name": "Tamil Nadu Express"}
]

@login_required
def dashboard(request):
    tasks = BookingTask.objects.filter(user=request.user).order_by('-id')
    return render(request, 'booking/dashboard.html', {'tasks': tasks})

@login_required
def add_task(request):
    if request.method == 'POST':
        form = BookingTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('dashboard')
    else:
        form = BookingTaskForm()
    return render(request, 'booking/add_task.html', {'form': form})

@csrf_exempt
def autocomplete_stations(request):
    """API endpoint for station autocomplete"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    filtered_stations = [
        station for station in INDIAN_STATIONS 
        if query.lower() in station.lower()
    ]
    
    return JsonResponse(filtered_stations[:10], safe=False)

@csrf_exempt
def autocomplete_trains(request):
    """API endpoint for train autocomplete"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    filtered_trains = []
    for train in INDIAN_TRAINS:
        if (query.lower() in train['name'].lower() or 
            query.lower() in train['number'].lower()):
            filtered_trains.append({
                'number': train['number'],
                'name': train['name'],
                'display': f"{train['number']} - {train['name']}"
            })
    
    return JsonResponse(filtered_trains[:10], safe=False)
