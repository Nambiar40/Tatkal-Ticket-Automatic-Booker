from django.urls import path
from . import views
from django.shortcuts import redirect 

urlpatterns = [
    path('', lambda request: redirect('login')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_booking_task, name='add_task'),
    path('signup/', views.signup, name='signup'),
]