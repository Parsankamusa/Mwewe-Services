from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model
from admindash.models import (
    Clients, Task, WeeklySchedule, VehicleRoute,
    Vehicles, Branches, DashboardItems
)
from admindash.utils.date_helpers import parse_date
from django.db.models import Count, Q, Avg
from collections import defaultdict
from datetime import datetime, timedelta
import csv
import json

User = get_user_model()


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def active_contracts_report(request):
    """Generate active contracts report."""
    # Role-based dashboard filtering
    data = DashboardItems.objects.all()
    if request.user.is_supervisor:
        data = data.exclude(id__in=[1, 2, 4, 5, 6, 8, 9])
    elif request.user.is_admin:
        data = data.exclude(id__in=[2, 4, 5, 8, 9])
    elif request.user.is_manager:
        data = data.exclude(id__in=[1, 3, 7, 8])

    data_list = list(data.values())

    # Get filter parameters
    region = request.GET.get('region', '')
    frequency = request.GET.get('frequency', '')
    status = request.GET.get('status', 'active')

    # Build query
    clients_query = Clients.objects.all()

    if region:
        clients_query = clients_query.filter(branch_asoc__icontains=region)

    if frequency:
        clients_query = clients_query.filter(billing_freq__iexact=frequency)

    # Filter by status
    today = datetime.now().date()
    if status == 'active':
        clients_query = clients_query.filter(
            Q(contract_end_date__gte=today) | Q(contract_end_date__isnull=True)
        )
    elif status == 'expired':
        clients_query = clients_query.filter(contract_end_date__lt=today)
    elif status == 'expiring_soon':
        next_30_days = today + timedelta(days=30)
        clients_query = clients_query.filter(
            contract_end_date__gte=today,
            contract_end_date__lte=next_30_days
        )

    # Generate report data
    contracts = []
    for client in clients_query:
        # Calculate days until expiry
        days_until_expiry = None
        if client.contract_end_date:
            delta = client.contract_end_date - today
            days_until_expiry = delta.days

        contracts.append({
            "id": client.id,
            "client_name": client.client_name,
            "email": client.email,
            "contact_phone": client.contact_phone,
            "branch": client.branch_asoc,
            "frequency": client.billing_freq,
            "quantity": client.quantity,
            "contract_start": client.contract_start_date.isoformat() if client.contract_start_date else None,
            "contract_end": client.contract_end_date.isoformat() if client.contract_end_date else None,
            "days_until_expiry": days_until_expiry,
            "status": "Active" if days_until_expiry and days_until_expiry > 0 else "Expired"
        })

    # Summary statistics
    total_contracts = len(contracts)
    total_bins = sum(c.get("quantity", 0) for c in contracts)
    avg_contract_value = total_bins / total_contracts if total_contracts > 0 else 0

    # Frequency breakdown
    freq_breakdown = defaultdict(int)
    for contract in contracts:
        freq_breakdown[contract.get("frequency", "Unknown")] += 1

    # Region breakdown
    region_breakdown = defaultdict(int)
    for contract in contracts:
        region_breakdown[contract.get("branch", "Unknown")] += 1

    return JsonResponse({
        "success": True,
        "dashboard": data_list,
        "report": {
            "contracts": contracts,
            "summary": {
                "total_contracts": total_contracts,
                "total_bins": total_bins,
                "avg_contract_value": round(avg_contract_value, 2),
                "frequency_breakdown": dict(freq_breakdown),
                "region_breakdown": dict(region_breakdown)
            },
            "filters": {
                "region": region,
                "frequency": frequency,
                "status": status
            }
        }
    })


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def task_report(request):
    """Generate task completion and performance report."""
    # Role-based dashboard filtering
    data = DashboardItems.objects.all()
    if request.user.is_supervisor:
        data = data.exclude(id__in=[1, 2, 4, 5, 6, 8, 9])
    elif request.user.is_admin:
        data = data.exclude(id__in=[2, 4, 5, 8, 9])
    elif request.user.is_manager:
        data = data.exclude(id__in=[1, 3, 7, 8])

    data_list = list(data.values())

    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    staff_id = request.GET.get('staff_id')
    status = request.GET.get('status')

    # Build query
    tasks_query = Task.objects.all()

    if start_date:
        start = parse_date(start_date)
        if start:
            tasks_query = tasks_query.filter(due_date__gte=start)

    if end_date:
        end = parse_date(end_date)
        if end:
            tasks_query = tasks_query.filter(due_date__lte=end)

    if staff_id:
        tasks_query = tasks_query.filter(staff_assigned=staff_id)

    if status:
        tasks_query = tasks_query.filter(status__iexact=status)

    # Generate task data
    tasks = []
    for task in tasks_query:
        tasks.append({
            "id": task.id,
            "client_name": task.client_name,
            "staff_assigned": task.staff_assigned,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "last_service_date": task.last_service_date.isoformat() if task.last_service_date else None,
            "status": task.status,
            "created_at": task.created_at.isoformat() if task.created_at else None,
        })

    # Calculate statistics
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.get("status", "").lower() == "completed")
    pending_tasks = sum(1 for t in tasks if t.get("status", "").lower() == "pending")
    overdue_tasks = sum(
        1 for t in tasks
        if t.get("due_date") and parse_date(t["due_date"]) < datetime.now().date()
        and t.get("status", "").lower() != "completed"
    )

    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Staff performance
    staff_performance = defaultdict(lambda: {"completed": 0, "pending": 0, "total": 0})
    for task in tasks:
        staff = task.get("staff_assigned", "Unassigned")
        staff_performance[staff]["total"] += 1
        if task.get("status", "").lower() == "completed":
            staff_performance[staff]["completed"] += 1
        else:
            staff_performance[staff]["pending"] += 1

    return JsonResponse({
        "success": True,
        "dashboard": data_list,
        "report": {
            "tasks": tasks,
            "summary": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "overdue_tasks": overdue_tasks,
                "completion_rate": round(completion_rate, 2)
            },
            "staff_performance": dict(staff_performance),
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "staff_id": staff_id,
                "status": status
            }
        }
    })


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def weekly_schedule_report(request):
    """Generate weekly schedule report."""
    # Role-based dashboard filtering
    data = DashboardItems.objects.all()
    if request.user.is_supervisor:
        data = data.exclude(id__in=[1, 2, 4, 5, 6, 8, 9])
    elif request.user.is_admin:
        data = data.exclude(id__in=[2, 4, 5, 8, 9])
    elif request.user.is_manager:
        data = data.exclude(id__in=[1, 3, 7, 8])

    data_list = list(data.values())

    # Get filter parameters
    week_start = request.GET.get('week_start')
    route = request.GET.get('route')

    # Build query
    schedules_query = WeeklySchedule.objects.all().order_by('-date_to_service')

    if week_start:
        start = parse_date(week_start)
        if start:
            week_end = start + timedelta(days=7)
            schedules_query = schedules_query.filter(
                date_to_service__gte=start,
                date_to_service__lt=week_end
            )

    if route:
        schedules_query = schedules_query.filter(route__icontains=route)

    # Generate schedule data
    schedules = []
    for schedule in schedules_query:
        schedules.append({
            "id": schedule.id,
            "route": schedule.route,
            "day_of_week": schedule.day_of_week,
            "client_name": schedule.client_name,
            "date_to_service": schedule.date_to_service.isoformat() if schedule.date_to_service else None,
            "staff_assigned": schedule.staff_assigned,
            "created_at": schedule.created_at.isoformat() if schedule.created_at else None,
        })

    # Group by day of week
    by_day = defaultdict(list)
    for schedule in schedules:
        by_day[schedule.get("day_of_week", "Unknown")].append(schedule)

    # Route statistics
    route_stats = defaultdict(lambda: {"count": 0, "clients": set()})
    for schedule in schedules:
        route_name = schedule.get("route", "Unknown")
        route_stats[route_name]["count"] += 1
        route_stats[route_name]["clients"].add(schedule.get("client_name"))

    # Convert sets to counts
    route_summary = {
        route: {
            "total_schedules": stats["count"],
            "unique_clients": len(stats["clients"])
        }
        for route, stats in route_stats.items()
    }

    return JsonResponse({
        "success": True,
        "dashboard": data_list,
        "report": {
            "schedules": schedules,
            "by_day": dict(by_day),
            "route_summary": route_summary,
            "summary": {
                "total_schedules": len(schedules),
                "unique_routes": len(route_stats),
                "unique_clients": len(set(s.get("client_name") for s in schedules))
            },
            "filters": {
                "week_start": week_start,
                "route": route
            }
        }
    })


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def staff_report(request):
    """Generate staff performance and workload report."""
    # Role-based dashboard filtering
    data = DashboardItems.objects.all()
    if request.user.is_supervisor:
        data = data.exclude(id__in=[1, 2, 4, 5, 6, 8, 9])
    elif request.user.is_admin:
        data = data.exclude(id__in=[2, 4, 5, 8, 9])
    elif request.user.is_manager:
        data = data.exclude(id__in=[1, 3, 7, 8])

    data_list = list(data.values())

    # Get all non-admin staff
    staff_query = User.objects.filter(is_staff=True).exclude(
        is_superuser=True
    ).exclude(
        username__in=["admin", "administrator"]
    )

    # Get filter parameters
    region = request.GET.get('region')
    specialization = request.GET.get('specialization')

    if region:
        staff_query = staff_query.filter(region__icontains=region)

    if specialization:
        staff_query = staff_query.filter(specialization__icontains=specialization)

    # Generate staff report
    staff_data = []
    for staff in staff_query:
        # Get task statistics
        total_tasks = Task.objects.filter(staff_assigned=staff.username).count()
        completed_tasks = Task.objects.filter(
            staff_assigned=staff.username,
            status__iexact="completed"
        ).count()
        pending_tasks = Task.objects.filter(
            staff_assigned=staff.username,
            status__iexact="pending"
        ).count()

        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Get scheduled routes
        scheduled_routes = WeeklySchedule.objects.filter(
            staff_assigned=staff.username
        ).count()

        staff_data.append({
            "id": staff.id,
            "username": staff.username,
            "email": staff.email,
            "region": getattr(staff, 'region', ''),
            "specialization": getattr(staff, 'specialization', ''),
            "phone": getattr(staff, 'phone', ''),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": round(completion_rate, 2),
            "scheduled_routes": scheduled_routes,
            "is_active": staff.is_active,
            "date_joined": staff.date_joined.isoformat() if staff.date_joined else None
        })

    # Calculate summary statistics
    total_staff = len(staff_data)
    active_staff = sum(1 for s in staff_data if s.get("is_active"))
    avg_completion_rate = sum(s.get("completion_rate", 0) for s in staff_data) / total_staff if total_staff > 0 else 0

    # Region distribution
    region_dist = defaultdict(int)
    for staff in staff_data:
        region_dist[staff.get("region", "Unknown")] += 1

    # Specialization distribution
    specialization_dist = defaultdict(int)
    for staff in staff_data:
        specialization_dist[staff.get("specialization", "Unknown")] += 1

    return JsonResponse({
        "success": True,
        "dashboard": data_list,
        "report": {
            "staff": staff_data,
            "summary": {
                "total_staff": total_staff,
                "active_staff": active_staff,
                "avg_completion_rate": round(avg_completion_rate, 2),
                "region_distribution": dict(region_dist),
                "specialization_distribution": dict(specialization_dist)
            },
            "filters": {
                "region": region,
                "specialization": specialization
            }
        }
    })


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def vehicle_utilization_report(request):
    """Generate vehicle utilization report."""
    # Role-based dashboard filtering
    data = DashboardItems.objects.all()
    if request.user.is_supervisor:
        data = data.exclude(id__in=[1, 2, 4, 5, 6, 8, 9])
    elif request.user.is_admin:
        data = data.exclude(id__in=[2, 4, 5, 8, 9])
    elif request.user.is_manager:
        data = data.exclude(id__in=[1, 3, 7, 8])

    data_list = list(data.values())

    # Get all vehicles
    vehicles = Vehicles.objects.all()

    vehicle_data = []
    for vehicle in vehicles:
        # Get route assignments
        total_assignments = VehicleRoute.objects.filter(plate=vehicle.vehicle_name).count()

        # Get unique routes covered
        unique_routes = VehicleRoute.objects.filter(
            plate=vehicle.vehicle_name
        ).values_list('route', flat=True).distinct().count()

        # Get total clients served
        total_clients = VehicleRoute.objects.filter(
            plate=vehicle.vehicle_name
        ).aggregate(total=Count('clients'))['total'] or 0

        # Calculate utilization rate (assignments vs capacity)
        utilization_rate = (total_clients / vehicle.capacity * 100) if vehicle.capacity > 0 else 0

        vehicle_data.append({
            "id": vehicle.id,
            "vehicle_name": vehicle.vehicle_name,
            "capacity": vehicle.capacity,
            "region": vehicle.region,
            "is_available": vehicle.is_available,
            "service_specializations": vehicle.service_specializations,
            "total_assignments": total_assignments,
            "unique_routes": unique_routes,
            "total_clients_served": total_clients,
            "utilization_rate": round(utilization_rate, 2)
        })

    # Summary statistics
    total_vehicles = len(vehicle_data)
    available_vehicles = sum(1 for v in vehicle_data if v.get("is_available"))
    avg_utilization = sum(v.get("utilization_rate", 0) for v in vehicle_data) / total_vehicles if total_vehicles > 0 else 0

    return JsonResponse({
        "success": True,
        "dashboard": data_list,
        "report": {
            "vehicles": vehicle_data,
            "summary": {
                "total_vehicles": total_vehicles,
                "available_vehicles": available_vehicles,
                "avg_utilization_rate": round(avg_utilization, 2)
            }
        }
    })


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def export_report_csv(request):
    """Export report data to CSV."""
    report_type = request.GET.get('type', 'contracts')

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)

    if report_type == 'contracts':
        # Export contracts
        writer.writerow([
            'Client Name', 'Email', 'Phone', 'Branch', 'Frequency',
            'Quantity', 'Contract Start', 'Contract End', 'Status'
        ])

        clients = Clients.objects.all()
        today = datetime.now().date()

        for client in clients:
            status = "Active"
            if client.contract_end_date and client.contract_end_date < today:
                status = "Expired"

            writer.writerow([
                client.client_name,
                client.email,
                client.contact_phone,
                client.branch_asoc,
                client.billing_freq,
                client.quantity,
                client.contract_start_date,
                client.contract_end_date,
                status
            ])

    elif report_type == 'tasks':
        # Export tasks
        writer.writerow([
            'Client Name', 'Staff Assigned', 'Due Date',
            'Last Service Date', 'Status', 'Created At'
        ])

        tasks = Task.objects.all()
        for task in tasks:
            writer.writerow([
                task.client_name,
                task.staff_assigned,
                task.due_date,
                task.last_service_date,
                task.status,
                task.created_at
            ])

    elif report_type == 'staff':
        # Export staff
        writer.writerow([
            'Username', 'Email', 'Phone', 'Region',
            'Specialization', 'Total Tasks', 'Completed Tasks',
            'Completion Rate', 'Status'
        ])

        staff = User.objects.filter(is_staff=True).exclude(is_superuser=True)
        for member in staff:
            total_tasks = Task.objects.filter(staff_assigned=member.username).count()
            completed_tasks = Task.objects.filter(
                staff_assigned=member.username,
                status__iexact="completed"
            ).count()
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            writer.writerow([
                member.username,
                member.email,
                getattr(member, 'phone', ''),
                getattr(member, 'region', ''),
                getattr(member, 'specialization', ''),
                total_tasks,
                completed_tasks,
                f"{completion_rate:.2f}%",
                "Active" if member.is_active else "Inactive"
            ])

    return response
