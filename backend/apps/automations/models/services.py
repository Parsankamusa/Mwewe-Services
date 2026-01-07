from django.db import models

class Services(models.Model):
    service_name = models.CharField(max_length=200)
    client_name = models.CharField(max_length=200)
    site_id = models.CharField(max_length=200)
    frequency = models.CharField(max_length=200)
    quantity = models.IntegerField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ServicesOffered(models.Model):
    name = models.CharField(max_length=200)
    alias = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)