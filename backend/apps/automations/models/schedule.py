from django.db import models

class WeeklySchedule(models.Model):
    region = models.CharField(max_length=200)
    weekday_name = models.CharField(max_length=200)
    route = models.CharField(max_length=200)
    client_name = models.CharField(max_length=200)
    date_to_service = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.region