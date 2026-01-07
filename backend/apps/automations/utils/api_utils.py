from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import models
from django.forms.models import model_to_dict
from datetime import datetime, date
import json


def serialize_model(instance):
    """
    Serialize a Django model instance to a dictionary
    """
    if instance is None:
        return None

    data = model_to_dict(instance)

    # Handle datetime and date fields
    for key, value in data.items():
        if isinstance(value, (datetime, date)):
            data[key] = value.isoformat()

    return data


def serialize_queryset(queryset):
    """
    Serialize a Django queryset to a list of dictionaries
    """
    return [serialize_model(instance) for instance in queryset]


def paginate_queryset(queryset, page_number=1, page_size=20):
    """
    Paginate a queryset and return pagination info
    """
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page_number)

    return {
        'results': list(page_obj),
        'pagination': {
            'page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'page_size': page_size
        }
    }


def api_response(data=None, message=None, success=True, status=200, errors=None):
    """
    Create a standardized API response
    """
    response_data = {
        'success': success,
    }

    if message:
        response_data['message'] = message

    if data is not None:
        response_data['data'] = data

    if errors:
        response_data['errors'] = errors

    return JsonResponse(response_data, status=status)


def api_error_response(message, status=400, errors=None, code=None):
    """
    Create a standardized API error response
    """
    response_data = {
        'success': False,
        'error': message
    }

    if code:
        response_data['code'] = code

    if errors:
        response_data['errors'] = errors

    return JsonResponse(response_data, status=status)


def handle_file_upload(request, file_field_name, allowed_extensions=None):
    """
    Handle file upload with validation
    """
    if file_field_name not in request.FILES:
        return None, "No file uploaded"

    uploaded_file = request.FILES[file_field_name]

    if allowed_extensions:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            return None, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"

    return uploaded_file, None


def validate_required_fields(data, required_fields):
    """
    Validate that required fields are present in the data
    """
    missing_fields = []

    for field in required_fields:
        if field not in data or data[field] in [None, '', []]:
            missing_fields.append(field)

    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    return True, None


def parse_date_string(date_string, default=None):
    """
    Parse date string to date object
    """
    if not date_string:
        return default

    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return default


def get_user_permissions(user):
    """
    Get user permissions and role information
    """
    return {
        'is_superuser': user.is_superuser,
        'is_admin': getattr(user, 'is_admin', False),
        'is_manager': getattr(user, 'is_manager', False),
        'is_supervisor': getattr(user, 'is_supervisor', False),
        'is_staff': user.is_staff,
        'is_active': user.is_active,
        'role_alias': getattr(user, 'role_alias', 'user')
    }


def filter_dashboard_items(user):
    """
    Filter dashboard items based on user role
    """
    from .models import DashboardItems

    data = DashboardItems.objects.all()

    if user.is_supervisor:
        data = data.exclude(id__in=[1, 2, 4, 5, 6, 8, 9])
    elif user.is_admin:
        data = data.exclude(id__in=[2, 4, 5, 8, 9])
    elif user.is_manager:
        data = data.exclude(id__in=[1, 3, 7, 8])

    return list(data.values())


class APIException(Exception):
    """
    Custom exception for API errors
    """

    def __init__(self, message, status=400, code=None):
        self.message = message
        self.status = status
        self.code = code
        super().__init__(self.message)