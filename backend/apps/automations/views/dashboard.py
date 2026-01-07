
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum, Max, Min, Avg
from collections import defaultdict
from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def admin(request):
    today = timezone.localdate()

    def parse_date(date_str, default=None):
        if not date_str:
            return default
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return default

    # client stats
    all_clients = Clients.objects.all()

    # Monthly Contracts Data
    monthly_counts = defaultdict(int)
    expired_count = 0
    renewal_count = 0
    active_count = 0
    prospect_count = 0

    for client in all_clients:
        start_date = parse_date(client.contract_start_date)
        end_date = parse_date(client.contract_end_date)

        # Monthly contract counts
        if start_date:
            month_year = start_date.strftime("%b %Y")
            monthly_counts[month_year] += 1

        # Contract status counts
        if client.is_prospect:
            prospect_count += 1
        elif end_date:
            if end_date < today:
                expired_count += 1
            else:
                active_count += 1
                if end_date <= today + timedelta(days=30):
                    renewal_count += 1

    # contract count
    monthly_data = [
        {"month": month, "count": count}
        for month, count in sorted(monthly_counts.items())
    ]

    # Frequency Breakdown
    freq_breakdown = list(
        Clients.objects.values("frequency").annotate(count=Count("id"))
    )

    # Region Breakdown
    region_breakdown = list(
        Clients.objects.values("region").annotate(count=Count("id"))
    )

    # Average bins calculation
    avg_bins = Clients.objects.aggregate(avg_bins=Avg("quantity"))["avg_bins"] or 0

    # 2. Task and Staff Statistics
    task_count = Task.objects.count()

    # Get staff count exclude administrative staff
    staff_queryset = User.objects.filter(is_staff=True).values(
        "username", "is_superuser", "is_admin", "is_manager", "is_supervisor"
    )
    non_admin_staff = [
        user
        for user in staff_queryset
        if not (
            user["is_superuser"]
            or user["is_manager"]
            or user["is_admin"]
            or user["is_supervisor"]
        )
    ]
    staff_count = len(non_admin_staff)

    # 3. Weekly Schedule Analytics
    recent_schedules = list(WeeklySchedule.objects.order_by("-created_at")[:5].values())
    route_breakdown = list(
        WeeklySchedule.objects.values("route").annotate(count=Count("id"))
    )
    upcoming_schedules = list(
        WeeklySchedule.objects.filter(
            date_to_service__gte=today, date_to_service__lte=today + timedelta(days=7)
        )
        .order_by("date_to_service")
        .values()
    )

    data = DashboardItems.objects.all()
    if request.user.is_supervisor:
        data = data.exclude(id__in=[1, 2, 4, 5, 6, 8, 9])
    elif request.user.is_admin:
        data = data.exclude(id__in=[2, 4, 5, 8, 9])
    elif request.user.is_manager:
        data = data.exclude(id__in=[1, 3, 7, 8])

    data_list = list(data.values())

    # return 20 recent activities
    recent_activity = list(
        RecentActivity.objects.all().order_by("-created_at").values()[:20]
    )

    response_data = {
        # Client statistics
        "total_contracts": all_clients.count(),
        "active_contracts": active_count,
        "expired_contracts": expired_count,
        "prospect_count": prospect_count,
        "avg_bins": round(avg_bins, 1),
        "renewal_count": renewal_count,
        "freq_breakdown": freq_breakdown,
        "region_breakdown": region_breakdown,
        "monthly_data": monthly_data,
        # Task and staff
        "task_count": task_count,
        "client_count": all_clients.count(),
        "staff_count": staff_count,
        # Weekly Schedule
        "recent_schedules": recent_schedules,
        "route_breakdown": route_breakdown,
        "upcoming_schedules": upcoming_schedules,
        "data": data_list,
        # Recent Activity
        "recent_activity": recent_activity,
        "success": True,
    }

    return JsonResponse(response_data)