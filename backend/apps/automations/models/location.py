from django.db import models

class SharedLocations(models.Model):
    region = models.CharField(max_length=200)
    sub_region = models.CharField(max_length=200)
    shared_loc = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.region + " - " + self.sub_region

    class Meta:
        verbose_name_plural = "Shared Locations"
        db_name = "shared_locations"

class SubRegion(models.Model):
    region = models.CharField(max_length=200)
    sub_region = models.CharField(max_length=200)
    routes_in_sub_region = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.region + " - " + self.sub_region
    class Meta:
        verbose_name_plural = "Sub Regions"
        db_table = "sub_regions"


class SpecialAcess(models.Model):
    company_name = models.CharField(max_length=200)
    allowed_staff = models.CharField(max_length=200, default="")
    comment = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name_plural = "Special Access"
        db_table = "special_access"


class SubregionAllowedStaff(models.Model):
    sub_region = models.CharField(max_length=200)
    allowed_staff = models.CharField(max_length=200, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sub_region
    class Meta:
        verbose_name_plural = "Subregion Allowed Staff"
        db_table = "subregion_allowed_staff"

class Branches(models.Model):
    branch_id = models.CharField(max_length=200)
    branch_name = models.CharField(max_length=200)
    route = models.CharField(max_length=200)
    town = models.CharField(max_length=200, default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.branch_name

    class Meta:
        verbose_name_plural = "Branches"
        db_table = "branches"

class FrequencySettings(models.Model):
    frequency_name = models.CharField(max_length=200, unique=True, help_text="Internal name (e.g., weekly, bi-weekly)")
    frequency_label = models.CharField(max_length=200, help_text="Display name for frontend")
    interval_days = models.IntegerField(help_text="Number of days between services.py")
    description = models.TextField(blank=True, default="", help_text="Description of this frequency")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.frequency_label} ({self.interval_days} days)"

    class Meta:
        verbose_name_plural = "Frequency Settings"
        db_table = "frequency_settings"
