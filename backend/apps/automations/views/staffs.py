from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from automations.services.data_loaders.file_processor import StaffFileProcessor
from automations.utils.validators import validate_required_fields, is_valid_email
import json

User = get_user_model()


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def show_staff(request):
    """List all staff members."""
    if request.method == "GET":
        staff = User.objects.filter(is_staff=True).values(
            "id", "username", "email", "phone", "region",
            "specialization", "is_active", "is_onleave"
        )

        return JsonResponse({
            "success": True,
            "staff": list(staff)
        })


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def register_staff(request):
    """Register a new staff member."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validate required fields
            required = ["username", "email", "phone", "region", "specialization"]
            is_valid, error = validate_required_fields(data, required)

            if not is_valid:
                return JsonResponse({"success": False, "error": error}, status=400)

            # Validate email format
            if not is_valid_email(data["email"]):
                return JsonResponse({
                    "success": False,
                    "error": "Invalid email format"
                }, status=400)

            # Check if username exists
            if User.objects.filter(username=data["username"]).exists():
                return JsonResponse({
                    "success": False,
                    "error": "Username already exists"
                }, status=400)

            # Create user
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                phone=data["phone"],
                region=data["region"],
                specialization=data["specialization"],
                is_staff=True,
                password=data.get("password", "defaultpassword123")
            )

            return JsonResponse({
                "success": True,
                "message": "Staff registered successfully",
                "staff_id": user.id
            }, status=201)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)


@require_POST
@csrf_exempt
@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def edit_staff(request):
    """Update staff member details."""
    try:
        data = json.loads(request.body)
        staff_id = data.get("staff_id")

        if not staff_id:
            return JsonResponse({
                "success": False,
                "error": "staff_id is required"
            }, status=400)

        staff = User.objects.get(id=staff_id)

        # Update fields
        updateable_fields = ["email", "phone", "region", "specialization", "is_active", "is_onleave"]

        for field in updateable_fields:
            if field in data:
                setattr(staff, field, data[field])

        staff.save()

        return JsonResponse({
            "success": True,
            "message": "Staff updated successfully"
        })

    except User.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Staff member not found"
        }, status=404)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@require_POST
@csrf_exempt
@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def delete_staff(request):
    """Delete staff member."""
    try:
        data = json.loads(request.body)
        staff_id = data.get("staff_id")

        staff = User.objects.get(id=staff_id)
        staff.delete()

        return JsonResponse({
            "success": True,
            "message": "Staff deleted successfully"
        })

    except User.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Staff member not found"
        }, status=404)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def upload_staff_file(request):
    """Process bulk staff upload from CSV/Excel."""
    if request.method == "POST":
        try:
            uploaded_file = request.FILES.get("file")

            if not uploaded_file:
                return JsonResponse({
                    "success": False,
                    "error": "No file provided"
                }, status=400)

            # Use service layer for file processing
            processor = StaffFileProcessor()
            result = processor.process_file(uploaded_file)

            return JsonResponse(result)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)
