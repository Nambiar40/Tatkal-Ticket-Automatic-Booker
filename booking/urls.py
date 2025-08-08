from django.urls import path
from . import views  # booking app views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # main dashboard
    path('add-task/', views.add_booking_task, name='add_task'),
    # Add other booking-related URLs here
]

