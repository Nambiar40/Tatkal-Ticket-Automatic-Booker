from django.contrib import admin
from django.urls import path, include
from accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('booking.urls')),
    path('accounts/', include('accounts.urls')),
    path('login/', account_views.login_view, name='login'),  # ✅ This ma
]
