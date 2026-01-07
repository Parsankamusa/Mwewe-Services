import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class HomeCustomize(models.Model):
    data_modified = models.CharField(max_length=200)
    newValue = models.CharField(max_length=200)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.data_modified


class Uploads(models.Model):
    caption = models.CharField(max_length=100, default="An image", null=False, blank=False)
    file_field = models.FileField(upload_to="media/", null=False, blank=False)

    def __str__(self):
        return self.caption


class DashboardItems(models.Model):
    name = models.CharField(max_length=200)
    button = models.TextField(default="", blank=True)
    subcat_1 = models.TextField(default="", blank=True, verbose_name="Subcategory 1 (HTML)")
    subcat_2 = models.TextField(default="", blank=True, verbose_name="Subcategory 2 (HTML)")
    subcat_3 = models.TextField(default="", blank=True, verbose_name="Subcategory 3 (HTML)")
    subcat_4 = models.TextField(default="", blank=True, verbose_name="Subcategory 4 (HTML)")
    subcat_5 = models.TextField(default="", blank=True, verbose_name="Subcategory 5 (HTML)")
    subcat_6 = models.TextField(default="", blank=True, verbose_name="Subcategory 6 (HTML)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name






class RecentActivity(models.Model):
    initiator_name = models.CharField(null=True, default="", max_length=200)
    action = models.CharField(max_length=200)
    details = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Workload(models.Model):
    staff_name = models.CharField(max_length=200)
    client_assigned = models.CharField(max_length=200)
    workload_count = models.IntegerField()
    date_assigned = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AuditTrail(models.Model):
    initiator = models.CharField(max_length=200)
    action = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




