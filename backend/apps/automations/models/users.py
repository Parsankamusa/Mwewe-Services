from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    updated_at = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=200, default="")
    region = models.CharField(max_length=200)
    is_admin = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    is_emergency = models.BooleanField(default=False)
    is_onleave = models.BooleanField(default=False)
    is_laidoff = models.BooleanField(default=False)
    has_special_access = models.BooleanField(default=False)
    role_alias = models.CharField(max_length=200)
    profile_image = models.CharField(max_length=200, default="")
    bio = models.CharField(max_length=200, default="", blank=True)
    service_specializations = models.JSONField(default=list, blank=True,
                                               help_text="List of services.py this staff can handle")
    can_handle_all_services = models.BooleanField(default=False, help_text="If True, staff can handle any service type")
    can_handle_all_subregions = models.BooleanField(default=False)

class Subcontractors(models.Model):
    company_name = models.CharField(max_length=200, null=True, default="")
    alias = models.CharField(max_length=200, null=True, default="")
    jobcard = models.CharField(max_length=200, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StaffAssignmentResult(models.Model):
    staff_name = models.CharField(max_length=200)
    sub_region = models.CharField(max_length=200)
    number_of_clients_assigned = models.IntegerField()
    clients_assigned = models.TextField()
    date_assigned = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TODOReassignments(models.Model):
    staff_assigned = models.CharField(max_length=200)
    client_assigned = models.CharField(max_length=200)
    reassigned_date = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UnassignedClients(models.Model):
    target_date = models.CharField(max_length=200)
    total_scheduled = models.IntegerField()
    total_assigned = models.IntegerField()
    total_unassigned = models.IntegerField()
    unassigned_clients = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
