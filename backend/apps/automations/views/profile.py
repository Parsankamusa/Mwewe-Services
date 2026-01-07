from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from utils.validators import is_valid_email, is_valid_phone
import json

User = get_user_model()


@login_required
def profile(request):
    """Get current user profile information."""
    user = request.user

    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": getattr(user, 'phone', ''),
        "region": getattr(user, 'region', ''),
        "specialization": getattr(user, 'specialization', ''),
        "is_supervisor": getattr(user, 'is_supervisor', False),
        "is_admin": getattr(user, 'is_admin', False),
        "is_manager": getattr(user, 'is_manager', False),
        "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }

    return JsonResponse({
        "success": True,
        "profile": user_data
    })


@require_POST
@csrf_exempt
@login_required
def update_profile(request):
    """Update current user profile."""
    try:
        data = json.loads(request.body)
        user = request.user

        # Update basic information
        if "first_name" in data:
            user.first_name = data["first_name"].strip()

        if "last_name" in data:
            user.last_name = data["last_name"].strip()

        # Validate and update email
        if "email" in data:
            email = data["email"].strip()
            if email and not is_valid_email(email):
                return JsonResponse({
                    "success": False,
                    "error": "Invalid email format"
                }, status=400)

            # Check if email is already taken by another user
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                return JsonResponse({
                    "success": False,
                    "error": "Email already in use"
                }, status=400)

            user.email = email

        # Validate and update phone
        if "phone" in data:
            phone = data["phone"].strip()
            if phone and not is_valid_phone(phone):
                return JsonResponse({
                    "success": False,
                    "error": "Invalid phone format. Use format: 0712345678"
                }, status=400)

            if hasattr(user, 'phone'):
                user.phone = phone

        # Update region
        if "region" in data and hasattr(user, 'region'):
            user.region = data["region"].strip()

        # Update specialization
        if "specialization" in data and hasattr(user, 'specialization'):
            user.specialization = data["specialization"].strip()

        # Handle password change
        if "current_password" in data and "new_password" in data:
            current_password = data["current_password"]
            new_password = data["new_password"]

            if not user.check_password(current_password):
                return JsonResponse({
                    "success": False,
                    "error": "Current password is incorrect"
                }, status=400)

            if len(new_password) < 8:
                return JsonResponse({
                    "success": False,
                    "error": "New password must be at least 8 characters"
                }, status=400)

            user.set_password(new_password)

        user.save()

        return JsonResponse({
            "success": True,
            "message": "Profile updated successfully",
            "profile": {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": getattr(user, 'phone', ''),
                "region": getattr(user, 'region', ''),
                "specialization": getattr(user, 'specialization', '')
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
            "error": f"Profile update failed: {str(e)}"
        }, status=500)


@login_required
def change_password(request):
    """Change user password (separate endpoint for security)."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user

            current_password = data.get("current_password")
            new_password = data.get("new_password")
            confirm_password = data.get("confirm_password")

            # Validation
            if not all([current_password, new_password, confirm_password]):
                return JsonResponse({
                    "success": False,
                    "error": "All password fields are required"
                }, status=400)

            if not user.check_password(current_password):
                return JsonResponse({
                    "success": False,
                    "error": "Current password is incorrect"
                }, status=400)

            if new_password != confirm_password:
                return JsonResponse({
                    "success": False,
                    "error": "New passwords do not match"
                }, status=400)

            if len(new_password) < 8:
                return JsonResponse({
                    "success": False,
                    "error": "Password must be at least 8 characters"
                }, status=400)

            # Password strength validation
            if not any(char.isdigit() for char in new_password):
                return JsonResponse({
                    "success": False,
                    "error": "Password must contain at least one number"
                }, status=400)

            if not any(char.isupper() for char in new_password):
                return JsonResponse({
                    "success": False,
                    "error": "Password must contain at least one uppercase letter"
                }, status=400)

            # Update password
            user.set_password(new_password)
            user.save()

            return JsonResponse({
                "success": True,
                "message": "Password changed successfully"
            })

        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": "Invalid JSON data"
            }, status=400)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": f"Password change failed: {str(e)}"
            }, status=500)

    return JsonResponse({
        "success": False,
        "error": "Only POST method allowed"
    }, status=405)
