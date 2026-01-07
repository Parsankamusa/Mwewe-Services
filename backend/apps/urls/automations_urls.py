"""
Main URL configuration for automations app.
Includes all sub-URL patterns from individual modules.
"""
from django.urls import path, include

app_name = 'automations'

urlpatterns = [
    # Dashboard
    path('dashboard/', include('urls.dashboard_urls')),

    # Branches
    path('branches/', include('urls.branch_urls')),

    # Notifications
    path('notifications/', include('urls.notification_urls')),

    # Profile
    path('profile/', include('urls.profile_urls')),

    # Reports
    path('reports/', include('urls.report_urls')),

    # Routes
    path('routes/', include('urls.route_urls')),

    # Services
    path('services/', include('urls.service_urls')),

    # Staff
    path('staff/', include('urls.staff_urls')),

    # Tasks
    path('tasks/', include('urls.task_urls')),

    # Vehicles
    path('vehicles/', include('urls.vehicle_urls')),
]

