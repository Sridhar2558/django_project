"""
URL configuration for eduquity_hardware project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def dashboard_redirect(request):
    """Redirect user to appropriate dashboard based on user type"""
    if request.user.is_authenticated:
        if request.user.user_type == 'manager':
            return redirect('manager_dashboard')
        else:
            return redirect('employee_dashboard')
    return redirect('login')

urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),
    
    # Redirect root URL to login or dashboard
    path('', dashboard_redirect, name='home'),
    
    # Include app URLs
    path('', include('hardware_management.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "Eduquity Hardware Management - Admin"
admin.site.site_title = "Eduquity Admin Portal"
admin.site.index_title = "Welcome to Eduquity Hardware Management System"