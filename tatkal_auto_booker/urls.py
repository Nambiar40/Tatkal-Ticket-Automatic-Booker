from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('login')),  # Root → Login page
    path('admin/', admin.site.urls),
    path('dashboard/', include('booking.urls')),  # ✅ Fixed from dashboard.urls → booking.urls
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout
      
]
