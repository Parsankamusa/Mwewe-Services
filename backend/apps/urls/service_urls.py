"""
URL patterns for service views.
"""
from django.urls import path
from automations.views import services

urlpatterns = [
    path('', services.show_services, name='show_services'),
]

