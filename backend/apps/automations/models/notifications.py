from django.db import models


class Notification(models.Model):
    staff_assigned = models.CharField(max_length=200)
    client_assigned = models.CharField(max_length=200)
    services = models.CharField(max_length=200)
    premise_location = models.CharField(max_length=200)
    frequency = models.CharField(max_length=200)
    description = models.CharField(max_length=200, default="")
    status = models.CharField(max_length=200)
    priority = models.CharField(max_length=200)
    due_date = models.CharField(max_length=200, null=True, default=None)
    time = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.staff_assigned

class OTPData(models.Model):
    otp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class NotificationTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('otp_email', 'OTP Email'),
        ('password_reset_email', 'Password Reset Email'),
        ('task_assignment_sms', 'Task Assignment SMS'),
        ('task_assignment_email', 'Task Assignment Email'),
        ('client_reminder_sms', 'Client Reminder SMS'),
        ('client_reminder_email', 'Client Reminder Email'),
        ('client_apology_sms', 'Client Apology SMS'),
        ('supervisor_summary_email', 'Supervisor Summary Email'),
        ('staff_notification_sms', 'Staff Notification SMS'),
        ('staff_notification_email', 'Staff Notification Email'),
    ]

    template_type = models.CharField(max_length=200, choices=TEMPLATE_TYPES, unique=True)
    template_name = models.CharField(max_length=200)
    subject = models.CharField(max_length=300, blank=True, default="")
    content = models.TextField()
    is_html = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    variables_help = models.TextField(blank=True, default="", help_text="Available variables for this template")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.template_name} ({self.template_type})"

class ToSendToStaff(models.Model):
    staff_assigned = models.CharField(max_length=200)
    vehicle_assigned = models.CharField(max_length=200)
    service_date = models.CharField(max_length=200)
    client_assigned = models.CharField(max_length=200)
    route = models.CharField(max_length=200, default="Not Found")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.staff_assigned


class ClientNotification(models.Model):
    company_name = models.CharField(max_length=200)
    next_service_date = models.CharField(max_length=200)
    reminder_date = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

class ClientToNotify(models.Model):
    company_name = models.CharField(max_length=200)
    next_service_date = models.CharField(max_length=200)
    reminder_date = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

class StaffToNotify(models.Model):
    staff_assigned = models.CharField(max_length=200)
    client_assigned = models.CharField(max_length=5000)
    reminder_date = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.staff_assigned

class SupervisorNotify(models.Model):
    date_sent = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)