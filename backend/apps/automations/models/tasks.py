from django.db import models


class Task(models.Model):
    staff_assigned = models.CharField(max_length=200, default="")
    client_assigned = models.CharField(max_length=200, default="")
    contact_person = models.CharField(max_length=200, default="")
    contact_phone = models.CharField(max_length=200, default="")
    email = models.CharField(max_length=200, default="")
    services = models.CharField(max_length=200)
    premise_location = models.CharField(max_length=200)
    route = models.CharField(max_length=200)
    frequency = models.CharField(max_length=200)
    description = models.CharField(max_length=200, default="")
    comment = models.CharField(max_length=200, default="")
    status = models.CharField(max_length=200, default="")
    priority = models.CharField(max_length=200, default="")
    last_service_date = models.CharField(max_length=200)
    due_date = models.CharField(max_length=200, null=True, default="")
    revised_date = models.CharField(max_length=200, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.staff_assigned


class AutotaskSwitch(models.Model):
    run_autotask_job = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.run_autotask_job)


class AutotaskSettings(models.Model):
    no_automation_weekday = models.IntegerField(default=5)
    required_staff_in_sub_region_max = models.IntegerField(default=4)
    required_staff_in_sub_region_mid = models.IntegerField(default=3)
    required_staff_in_sub_region_low = models.IntegerField(default=2)
    count_of_client_in_subregion_to_assign_low = models.IntegerField(default=10)
    required_staff_in_sub_region_lowest = models.IntegerField(default=1)
    required_staff_more_bins = models.IntegerField(default=2)
    max_num_bins = models.IntegerField(default=25)
    default_working_staff = models.IntegerField(default=1)
    service_check = models.CharField(max_length=200, default="sanitary_bins")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.service_check