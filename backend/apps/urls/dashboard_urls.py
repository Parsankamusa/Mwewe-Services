"""
URL patterns for dashboard views.
"""
from django.urls import path
from automations.views import dashboard

urlpatterns = [
    path('admin/', dashboard.admin, name='admin_dashboard'),
]

