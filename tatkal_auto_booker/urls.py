from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect  # ✅ you need this for redirect

urlpatterns = [
    path('', lambda request: redirect('dashboard')),  # ✅ redirect root to /dashboard/
    path('admin/', admin.site.urls),
    path('dashboard/', include('booking.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
