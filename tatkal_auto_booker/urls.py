from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
import os

# Get the absolute path to staticfiles directory
static_root = os.path.join(settings.BASE_DIR, 'staticfiles')
media_root = os.path.join(settings.BASE_DIR, 'media')

urlpatterns = [
    path('', lambda request: redirect('login')),  # redirect root to login
    path('admin/', admin.site.urls),
    path('dashboard/', include('booking.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # for logout 
]

# Always serve static files in development
urlpatterns += static(settings.STATIC_URL, document_root=static_root)
urlpatterns += static(settings.MEDIA_URL, document_root=media_root)

