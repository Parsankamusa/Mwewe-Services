from django.db import models

class Vehicles(models.Model):
    vehicle_name = models.CharField(null=True, default=None, max_length=200)
    capacity = models.IntegerField(null=True, default=None)
    region = models.CharField(null=True, default=None, max_length=200)
    is_available = models.BooleanField(default=True)
    service_specializations = models.JSONField(default=list, blank=True,
                                               help_text="List of services.py this vehicle can handle")
    can_handle_all_services = models.BooleanField(default=False,
                                                  help_text="If True, vehicle can handle any service type")
    can_handle_all_subregions = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UnassignedVehicles(models.Model):
    region = models.CharField(max_length=200)
    route_name = models.CharField(max_length=200)
    client = models.CharField(max_length=5000)
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)