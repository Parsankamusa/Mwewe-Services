from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from admindash.models import Branches, DashboardItems
from admindash.services.data_loaders.file_processor import BranchFileProcessor
import json


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def show_branches(request):
    """List all branches."""
    data = DashboardItems.objects.all()

    if request.user.is_supervisor:
        data = data.exclude(id__in=[1, 2, 4, 5, 6, 8, 9])
    elif request.user.is_admin:
        data = data.exclude(id__in=[2, 4, 5, 8, 9])
    elif request.user.is_manager:
        data = data.exclude(id__in=[1, 3, 7, 8])

    data_list = list(data.values())
    branches = list(Branches.objects.all().values())

    return JsonResponse({
        "success": True,
        "dashboard": data_list,
        "branches": branches
    })


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def add_branch(request):
    """Add a new branch."""
    if request.method == "POST":
        data = json.loads(request.body)

        branch_name = data.get("branch_name")
        route = data.get("route")
        town = data.get("town", "")

        branch, created = Branches.objects.get_or_create(
            branch_name=branch_name,
            route=route,
            defaults={"town": town}
        )

        if created:
            return JsonResponse({
                "success": True,
                "message": "Branch added successfully",
                "branch": {
                    "id": branch.id,
                    "branch_name": branch.branch_name,
                    "route": branch.route,
                    "town": branch.town
                }
            }, status=201)
        else:
            return JsonResponse({
                "success": False,
                "error": "Branch already exists"
            }, status=400)

    return JsonResponse({
        "success": False,
        "error": "Only POST method allowed"
    }, status=405)


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def upload_branch_file(request):
    """Process bulk branch upload from CSV/Excel."""
    if request.method == "POST":
        try:
            uploaded_file = request.FILES.get("file")

            if not uploaded_file:
                return JsonResponse({
                    "success": False,
                    "error": "No file provided"
                }, status=400)

            processor = BranchFileProcessor()
            result = processor.process_file(uploaded_file)

            return JsonResponse(result)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)

    return JsonResponse({
        "success": False,
        "error": "Only POST method allowed"
    }, status=405)


@require_POST
@csrf_exempt
@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def edit_branch(request, branch_id):
    """Update branch details."""
    try:
        branch = Branches.objects.get(id=branch_id)
        data = json.loads(request.body)

        branch.branch_name = data.get("branch_name", branch.branch_name)
        branch.route = data.get("route", branch.route)
        branch.town = data.get("town", branch.town)

        branch.save()

        return JsonResponse({
            "success": True,
            "message": "Branch updated successfully",
            "branch": {
                "id": branch.id,
                "branch_name": branch.branch_name,
                "route": branch.route,
                "town": branch.town
            }
        })

    except Branches.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Branch not found"
        }, status=404)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@csrf_exempt
@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def delete_branch(request):
    """Delete a branch."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            branch_id = data.get("branch_id")

            branch = Branches.objects.get(id=branch_id)
            branch.delete()

            return JsonResponse({
                "success": True,
                "message": "Branch deleted successfully"
            })

        except Branches.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Branch not found"
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
