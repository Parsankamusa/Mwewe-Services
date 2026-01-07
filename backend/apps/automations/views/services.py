from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from admindash.models import Services, DashboardItems


@login_required
@permission_required("admindash.is_admin_member", raise_exception=True)
def show_services(request):
    """List all services."""
    data = DashboardItems.objects.all()

    if request.user.is_supervisor:
        data = data.exclude(id__in=[1, 2, 4, 5, 6, 8, 9])
    elif request.user.is_admin:
        data = data.exclude(id__in=[2, 4, 5, 8, 9])
    elif request.user.is_manager:
        data = data.exclude(id__in=[1, 3, 7, 8])

    data_list = list(data.values())
    services = list(Services.objects.all().values())

    return JsonResponse({
        "success": True,
        "dashboard": data_list,
        "services": services
    })
