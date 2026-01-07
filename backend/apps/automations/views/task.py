from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from models import Task, Clients, DashboardItems, TODOReassignments
from admindash.services.notifications.email import EmailService
from admindash.services.notifications.sms import SMSService
from utils.validators import validate_required_fields
from utils.date_helper import parse_date
import json
import threading

User = get_user_model()


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def show_tasks(request):
    """List all tasks."""
    if request.method == "GET":
        data = DashboardItems.objects.all()

        if request.user.is_supervisor:
            data = data.exclude(id__in=[1, 2, 4, 5, 6, 8, 9])
        elif request.user.is_admin:
            data = data.exclude(id__in=[2, 4, 5, 8, 9])
        elif request.user.is_manager:
            data = data.exclude(id__in=[1, 3, 7, 8])

        data_list = list(data.values())
        users = list(User.objects.all().values())
        tasks = list(Task.objects.all().order_by("-created_at").values())
        clients = list(Clients.objects.all().values())

        return JsonResponse({
            "success": True,
            "dashboard": data_list,
            "users": users,
            "tasks": tasks,
            "clients": clients
        })


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def assign_task(request):
    """Assign a task to staff."""
    if request.method == "GET":
        return JsonResponse({
            "success": False,
            "error": "GET method not supported. Use POST to assign tasks."
        }, status=405)

    elif request.method == "POST":
        data = json.loads(request.body)

        try:
            # Validate required fields
            required_fields = [
                "username", "client_id", "description",
                "status", "priority", "due_date"
            ]
            is_valid, error = validate_required_fields(data, required_fields)

            if not is_valid:
                return JsonResponse({
                    "success": False,
                    "error": error
                }, status=400)

            # Get staff and client
            staff = User.objects.get(username=data["username"])
            client = Clients.objects.get(id=data["client_id"])

            # Create task
            task = Task.objects.create(
                staff_assigned=data["username"],
                client_assigned=client.company_name,
                description=data["description"],
                status=data["status"],
                priority=data.get("priority", "Medium"),
                due_date=data["due_date"],
                last_service_date=data.get("last_service_date")
            )

            # Send notifications in background
            notification_thread = threading.Thread(
                target=_send_task_notifications,
                args=(staff, client, task.due_date)
            )
            notification_thread.start()

            return JsonResponse({
                "success": True,
                "message": "Task assigned successfully",
                "task_id": task.id
            }, status=201)

        except User.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Staff member not found"
            }, status=404)

        except Clients.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Client not found"
            }, status=404)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)


def _send_task_notifications(staff, client, due_date):
    """Send task assignment notifications."""
    try:
        email_service = EmailService()
        sms_service = SMSService()

        # Staff notification
        staff_message = (
            f"Hi {staff.username}, you're assigned to service: {client.company_name} "
            f"on {client.premise_location}, {due_date}."
        )

        if staff.email:
            email_service.send(
                recipient=staff.email,
                subject="New Task Assignment",
                content=staff_message
            )

        if staff.phone:
            sms_service.send(staff.phone, staff_message)

        # Client notification
        client_message = (
            f"Hello {client.company_name}, your {client.services_required} "
            f"is due on {due_date}.\n\nThank you"
        )

        if client.email:
            email_service.send(
                recipient=client.email,
                subject="Service Schedule",
                content=client_message
            )

        if client.contact_phone:
            sms_service.send(client.contact_phone, client_message)

    except Exception as e:
        print(f"Notification error: {e}")


@require_POST
@csrf_exempt
@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def edit_task(request, task_id):
    """Update task details."""
    try:
        task = Task.objects.get(id=task_id)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": "Invalid JSON"
            }, status=400)

        # Get initial values for change detection
        initial_due_date = None
        try:
            initial_due_date = task.due_date
        except (ValueError, TypeError):
            pass

        initial_staff_assigned = task.staff_assigned

        # Update task fields
        task.staff_assigned = data.get("staff_assigned", task.staff_assigned)
        task.status = data.get("status", task.status)

        # Handle last_service_date
        last_service_date_str = data.get("last_service_date")
        if last_service_date_str:
            task.last_service_date = parse_date(last_service_date_str)

        # Handle due_date
        due_date_str = data.get("due_date")
        if due_date_str:
            task.due_date = parse_date(due_date_str)

        task.save()

        # Send notifications if initial_due_date exists
        if initial_due_date:
            notification_thread = threading.Thread(
                target=_notify_task_changes,
                args=(task, initial_staff_assigned)
            )
            notification_thread.start()

        return JsonResponse({
            "success": True,
            "message": "Task updated successfully",
            "task": {
                "id": task.id,
                "staff_assigned": task.staff_assigned,
                "status": task.status,
                "due_date": str(task.due_date)
            }
        })

    except Task.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Task not found"
        }, status=404)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


def _notify_task_changes(task, initial_staff_assigned):
    """Handle task change notifications."""
    try:
        # Store reassignment for future use
        lookup_fields = {
            'client_assigned': task.client_assigned,
            'reassigned_date': task.revised_date,
        }
        defaults = {
            'staff_assigned': task.staff_assigned,
        }
        TODOReassignments.objects.update_or_create(**lookup_fields, defaults=defaults)

        # Check if staff assignment changed
        if task.staff_assigned != initial_staff_assigned:
            try:
                new_staff = User.objects.get(username=task.staff_assigned)
                client = Clients.objects.get(company_name=task.client_assigned)

                _send_task_notifications(new_staff, client, task.due_date)

            except (User.DoesNotExist, Clients.DoesNotExist) as e:
                print(f"Notification skipped: {e}")

        print("Notification thread completed")

    except Exception as e:
        print(f"Notification error: {e}")


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def task_approval(request):
    if request.method == "GET":
        # Get tasks that are not completed (Pending or In Progress)
        tasks = list(
            Task.objects.exclude(status="Completed").order_by("-created_at").values()
        )

        data = DashboardItems.objects.all()
        if request.user.is_supervisor:
            data = data.exclude(id__in=[1, 2, 4, 5, 6, 8, 9])
        elif request.user.is_admin:
            data = data.exclude(id__in=[2, 4, 5, 8, 9])
        elif request.user.is_manager:
            data = data.exclude(id__in=[1, 3, 7, 8])

        data_list = list(data.values())

        return JsonResponse(
            {
                "success": True,
                "tasks": tasks,
                "data": data_list,
            }
        )

@csrf_exempt
@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def delete_task(request):
    """Delete a task."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            task_id = data.get("task_id")

            task = Task.objects.get(id=task_id)
            task.delete()

            return JsonResponse({
                "success": True,
                "message": "Task deleted successfully"
            })

        except Task.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Task not found"
            }, status=404)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)

    return JsonResponse({
        "success": False,
        "error": "Only POST method allowed"
    }, status=405)
