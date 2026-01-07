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


class VehicleRoute(models.Model):
    plate = models.CharField(max_length=200)
    route = models.CharField(max_length=200)
    client = models.CharField(max_length=200)
    region = models.CharField(max_length=200)
    date_assigned = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.plate} - {self.route}"

    class Meta:
        verbose_name_plural = "Vehicle Routes"
        db_table = "vehicle_routes"
