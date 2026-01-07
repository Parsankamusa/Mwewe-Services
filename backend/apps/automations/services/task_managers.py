from datetime import datetime, timedelta
from django.db import transaction
from  automations.models import Task, Notification, Clients, User, Workload
from ..utils.validators import validate_staff_availability, StaffValidationError
from .notifications import send_mail, send_sms_staff, send_sms_client


@transaction.atomic
def assigned_task(username, client_id, description, status, priority, due_date):
    """Manually assign task to staff member with validation."""

    # Validate staff availability
    try:
        staff_member = validate_staff_availability(username)
    except StaffValidationError as e:
        raise ValueError(f"Cannot assign task: {e}")

    # Get client details
    client = Clients.objects.filter(contract_id=client_id).values(
        'services_required', 'frequency', 'premise_location', 'company_name'
    ).first()

    if not client:
        raise ValueError(f"No client found with contract_id: {client_id}")

    # Create task
    task = Task.objects.create(
        staff_assigned=username,
        client_assigned=client['company_name'],
        services=client['services_required'],
        frequency=client['frequency'],
        premise_location=client['premise_location'],
        description=description,
        status=status,
        priority=priority,
        due_date=due_date
    )

    # Create notification
    Notification.objects.create(
        staff_assigned=username,
        client_assigned=client_id,
        services=client['services_required'],
        frequency=client['frequency'],
        premise_location=client['premise_location'],
        description=description,
        due_date=due_date,
        priority=priority,
        status=status
    )

    # Send notifications (optional)
    _send_assignment_notifications(username, client['company_name'], due_date)

    return task


def _send_assignment_notifications(username, company_name, due_date):
    """Send email/SMS notifications for task assignment."""
    user = User.objects.get(username=username)
    client = Clients.objects.get(company_name=company_name)

    # Staff notification
    if user.email or user.phone:
        message = (
            f"Hi {user.username}, you're assigned to service: {company_name} "
            f"on {client.premise_location}, {due_date}."
        )
        # Uncomment to enable
        # if user.email:
        #     send_mail(user.email, message, "New Task Assigned")
        # if user.phone:
        #     send_sms_staff(user.phone, message)

    # Client notification
    if client.email or client.contact_phone:
        message = (
            f"Hello {client.company_name}, your {client.services_required} "
            f"is due on {due_date}.\n\nThank you"
        )
        # Uncomment to enable
        # if client.email:
        #     send_mail(client.email, message, f"Your Upcoming Cleaning Appointment – {client.company_name}")
        # if client.contact_phone:
        #     send_sms_client(client.contact_phone, due_date, client)
