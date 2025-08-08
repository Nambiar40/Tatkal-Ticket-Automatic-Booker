from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('login')),  # redirect root to login
    path('admin/', admin.site.urls),
    path('dashboard/', include('booking.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # built-in login/logout
]
