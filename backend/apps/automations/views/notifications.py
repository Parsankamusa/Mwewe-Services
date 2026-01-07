from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from models import Notification, DashboardItems
from admindash.services.notifications.email import EmailService
from admindash.services.notifications.sms import SMSService
from django.core.paginator import Paginator
import json


@login_required
def notifications(request):
    """Get user notifications with pagination."""
    # Role-based dashboard filtering
    data = DashboardItems.objects.all()
    if request.user.is_supervisor:
        data = data.exclude(id__in=[1, 2, 4, 5, 6, 8, 9])
    elif request.user.is_admin:
        data = data.exclude(id__in=[2, 4, 5, 8, 9])
    elif request.user.is_manager:
        data = data.exclude(id__in=[1, 3, 7, 8])

    data_list = list(data.values())

    # Get notifications for current user
    user_notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    # Pagination
    page_number = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 20)

    paginator = Paginator(user_notifications, per_page)
    page_obj = paginator.get_page(page_number)

    notifications_data = []
    for notification in page_obj:
        notifications_data.append({
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.notification_type,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat(),
            "related_task_id": notification.related_task_id,
            "related_client_id": notification.related_client_id,
        })

    # Count unread notifications
    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return JsonResponse({
        "success": True,
        "dashboard": data_list,
        "notifications": notifications_data,
        "unread_count": unread_count,
        "pagination": {
            "total_items": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "per_page": int(per_page),
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous()
        }
    })


@require_POST
@csrf_exempt
@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )

        notification.is_read = True
        notification.save()

        return JsonResponse({
            "success": True,
            "message": "Notification marked as read"
        })

    except Notification.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Notification not found"
        }, status=404)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@require_POST
@csrf_exempt
@login_required
def mark_all_notifications_read(request):
    """Mark all user notifications as read."""
    try:
        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return JsonResponse({
            "success": True,
            "message": f"Marked {updated_count} notifications as read"
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@require_POST
@csrf_exempt
@login_required
def delete_notification(request, notification_id):
    """Delete a notification."""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )

        notification.delete()

        return JsonResponse({
            "success": True,
            "message": "Notification deleted successfully"
        })

    except Notification.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Notification not found"
        }, status=404)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def send_bulk_notification(request):
    """Send bulk notifications to multiple users."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            recipient_type = data.get("recipient_type")  # "all", "supervisors", "staff", "specific"
            recipient_ids = data.get("recipient_ids", [])  # For specific users
            title = data.get("title")
            message = data.get("message")
            notification_type = data.get("type", "info")
            send_email = data.get("send_email", False)
            send_sms = data.get("send_sms", False)

            # Validation
            if not all([title, message]):
                return JsonResponse({
                    "success": False,
                    "error": "Title and message are required"
                }, status=400)

            # Determine recipients
            from django.contrib.auth import get_user_model
            User = get_user_model()

            if recipient_type == "all":
                recipients = User.objects.filter(is_active=True)
            elif recipient_type == "supervisors":
                recipients = User.objects.filter(is_supervisor=True, is_active=True)
            elif recipient_type == "staff":
                recipients = User.objects.filter(is_staff=True, is_active=True)
            elif recipient_type == "specific":
                recipients = User.objects.filter(id__in=recipient_ids, is_active=True)
            else:
                return JsonResponse({
                    "success": False,
                    "error": "Invalid recipient type"
                }, status=400)

            # Create notifications
            notifications_created = 0
            emails_sent = 0
            sms_sent = 0

            email_service = EmailService()
            sms_service = SMSService()

            for user in recipients:
                # Create in-app notification
                Notification.objects.create(
                    user=user,
                    title=title,
                    message=message,
                    notification_type=notification_type
                )
                notifications_created += 1

                # Send email if requested
                if send_email and user.email:
                    success, _ = email_service.send(
                        recipient=user.email,
                        subject=title,
                        content=message,
                        is_html=False
                    )
                    if success:
                        emails_sent += 1

                # Send SMS if requested
                if send_sms and hasattr(user, 'phone') and user.phone:
                    success, _ = sms_service.send(
                        phone=user.phone,
                        message=f"{title}: {message}"
                    )
                    if success:
                        sms_sent += 1

            return JsonResponse({
                "success": True,
                "message": "Bulk notification sent successfully",
                "stats": {
                    "notifications_created": notifications_created,
                    "emails_sent": emails_sent,
                    "sms_sent": sms_sent
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": "Invalid JSON data"
            }, status=400)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)

    return JsonResponse({
        "success": False,
        "error": "Only POST method allowed"
    }, status=405)
