from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from models.vehicles import Vehicles
from models.location import Branches
from models.common import DashboardItems
from admindash.services.data_loaders.file_processor import VehicleFileProcessor
import json


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def show_vehicles(request):
    """List all vehicles."""
    data = DashboardItems.objects.all()

    if request.user.is_supervisor:
        data = data.exclude(id__in=[1, 2, 4, 5, 6, 8, 9])
    elif request.user.is_admin:
        data = data.exclude(id__in=[2, 4, 5, 8, 9])
    elif request.user.is_manager:
        data = data.exclude(id__in=[1, 3, 7, 8])

    data_list = list(data.values())

    vehicles = list(Vehicles.objects.all().values(
        'id', 'vehicle_name', 'capacity', 'region', 'is_available',
        'service_specializations', 'can_handle_all_services',
        'can_handle_all_subregions', 'created_at', 'updated_at'
    ))

    unique_regions = list(
        Branches.objects.values_list("branch_name", flat=True)
        .distinct()
        .order_by("branch_name")
    )

    return JsonResponse({
        "success": True,
        "dashboard": data_list,
        "vehicles": vehicles,
        "regions": unique_regions
    })


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def add_vehicle(request):
    """Add a new vehicle."""
    if request.method == "POST":
        data = json.loads(request.body)

        vehicle_name = data.get("vehicle_name")
        capacity = data.get("capacity")
        region = data.get("region")
        service_specializations = data.get("service_specializations", [])
        can_handle_all_services = data.get("can_handle_all_services", False)

        if not isinstance(service_specializations, list):
            service_specializations = []

        vehicle, created = Vehicles.objects.get_or_create(
            vehicle_name=vehicle_name,
            defaults={
                "capacity": capacity,
                "region": region,
                "service_specializations": service_specializations,
                "can_handle_all_services": can_handle_all_services
            }
        )

        if created:
            return JsonResponse({
                "success": True,
                "message": "Vehicle added successfully",
                "vehicle": {
                    "id": vehicle.id,
                    "vehicle_name": vehicle.vehicle_name,
                    "capacity": vehicle.capacity,
                    "region": vehicle.region
                }
            }, status=201)
        else:
            return JsonResponse({
                "success": False,
                "error": "Vehicle already exists"
            }, status=400)

    return JsonResponse({
        "success": False,
        "error": "Only POST method allowed"
    }, status=405)


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def upload_vehicles_file(request):
    """Process bulk vehicle upload from CSV/Excel."""
    if request.method == "POST":
        try:
            uploaded_file = request.FILES.get("file")

            if not uploaded_file:
                return JsonResponse({
                    "success": False,
                    "error": "No file provided"
                }, status=400)

            processor = VehicleFileProcessor()
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
def edit_vehicle(request, vehicle_id):
    """Update vehicle details."""
    try:
        vehicle = Vehicles.objects.get(id=vehicle_id)
        data = json.loads(request.body)

        vehicle.vehicle_name = data.get("vehicle_name", vehicle.vehicle_name)
        vehicle.capacity = data.get("capacity", vehicle.capacity)
        vehicle.region = data.get("region", vehicle.region)

        service_specializations = data.get("service_specializations", [])
        can_handle_all_services = data.get("can_handle_all_services", False)
        can_handle_all_subregions = data.get("can_handle_all_subregions", False)

        if service_specializations is not None:
            vehicle.service_specializations = service_specializations

        if can_handle_all_services is not None:
            vehicle.can_handle_all_services = can_handle_all_services

        if can_handle_all_subregions is not None:
            vehicle.can_handle_all_subregions = can_handle_all_subregions

        status = data.get("is_available")
        if status == "true":
            vehicle.is_available = True
        elif status == "false":
            vehicle.is_available = False

        vehicle.save()

        return JsonResponse({
            "success": True,
            "message": "Vehicle updated successfully",
            "vehicle": {
                "id": vehicle.id,
                "vehicle_name": vehicle.vehicle_name,
                "capacity": vehicle.capacity,
                "region": vehicle.region,
                "is_available": vehicle.is_available
            }
        })

    except Vehicles.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Vehicle not found"
        }, status=404)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@csrf_exempt
@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def delete_vehicle(request):
    """Delete a vehicle."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            vehicle_id = data.get("vehicle_id")

            vehicle = Vehicles.objects.get(id=vehicle_id)
            vehicle.delete()

            return JsonResponse({
                "success": True,
                "message": "Vehicle deleted successfully"
            })

        except Vehicles.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Vehicle not found"
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
