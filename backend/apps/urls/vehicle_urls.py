"""
URL patterns for vehicle management views.
"""
from django.urls import path
from automations.views import vehicles

urlpatterns = [
    path('', vehicles.show_vehicles, name='show_vehicles'),
    path('add/', vehicles.add_vehicle, name='add_vehicle'),
    path('upload/', vehicles.upload_vehicles_file, name='upload_vehicles_file'),
    path('<int:vehicle_id>/edit/', vehicles.edit_vehicle, name='edit_vehicle'),
    path('delete/', vehicles.delete_vehicle, name='delete_vehicle'),
]

