from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-task/', views.add_task, name='add_task'),
    path('booking-details/', views.booking_details, name='booking_details'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('autocomplete/stations/', views.autocomplete_stations, name='autocomplete_stations'),
    path('autocomplete/trains/', views.autocomplete_trains, name='autocomplete_trains'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
]

