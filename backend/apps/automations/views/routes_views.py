from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from models.common import DashboardItems
from models.location import Branches
from models.vehicles import Vehicles
from models import VehicleRoute
from collections import defaultdict
import json


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def show_routes(request):
    """List all vehicle routes with clustering."""
    # Role-based dashboard filtering
    data = DashboardItems.objects.all()

    if request.user.is_supervisor:
        data = data.exclude(id__in=[1, 2, 4, 5, 6, 8, 9])
    elif request.user.is_admin:
        data = data.exclude(id__in=[2, 4, 5, 8, 9])
    elif request.user.is_manager:
        data = data.exclude(id__in=[1, 3, 7, 8])

    data_list = list(data.values())

    # Get assignments and cluster by vehicle, route, and date
    assignments = VehicleRoute.objects.all().order_by(
        "-service_date", "plate", "route", "clients"
    )

    clustered_data = defaultdict(lambda: {"region": "", "clients": []})

    for assign in assignments:
        key = (assign.plate, assign.route, assign.service_date)
        clustered_data[key]["region"] = assign.region.title()
        clustered_data[key]["clients"].append(assign.clients)

    # Convert to list for JSON serialization
    vehicle_enroute_data = []
    for key, value in clustered_data.items():
        plate, route, service_date = key
        vehicle_enroute_data.append({
            "plate": plate,
            "route": route,
            "service_date": str(service_date),
            "region": value["region"],
            "clients": value["clients"]
        })

    # Get unique values for filters
    unique_vehicles = list(
        Vehicles.objects.values_list("vehicle_name", flat=True)
        .distinct()
        .order_by("vehicle_name")
    )

    unique_regions = list(
        Branches.objects.values_list("branch_name", flat=True)
        .distinct()
        .order_by("branch_name")
    )

    unique_routes = list(
        Branches.objects.values_list("route", flat=True)
        .distinct()
        .order_by("route")
    )

    return JsonResponse({
        "success": True,
        "dashboard": data_list,
        "routes": vehicle_enroute_data,
        "vehicles": unique_vehicles,
        "regions": unique_regions,
        "available_routes": unique_routes
    })


@require_POST
@csrf_exempt
@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def edit_route(request, route_id):
    """Update route details."""
    try:
        route = VehicleRoute.objects.get(id=route_id)
        data = json.loads(request.body)

        route.route = data.get("route", route.route)
        route.clients = data.get("clients", route.clients)
        route.plate = data.get("plate", route.plate)

        route.save()

        return JsonResponse({
            "success": True,
            "message": "Route updated successfully",
            "route": {
                "id": route.id,
                "region": route.region,
                "route": route.route,
                "sites_covered": route.clients,
                "assigned_vehicles": route.plate
            }
        })

    except VehicleRoute.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Route not found"
        }, status=404)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@csrf_exempt
@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def delete_route(request):
    """Delete a route."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            route_id = data.get("route_id")

            route_data = VehicleRoute.objects.get(id=route_id)
            route_name = route_data.route
            route_data.delete()

            return JsonResponse({
                "success": True,
                "message": f"Route '{route_name}' deleted successfully"
            })

        except VehicleRoute.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Route not found"
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
