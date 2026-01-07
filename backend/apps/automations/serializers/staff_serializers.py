from typing import Dict, Any
from django.contrib.auth import get_user_model

User = get_user_model()


class StaffSerializer:
    """Serialize staff/user model instances."""

    @staticmethod
    def to_dict(user: User) -> Dict[str, Any]:
        """Convert user instance to dictionary."""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "region": user.region,
            "specialization": user.specialization,
            "is_active": user.is_active,
            "is_onleave": user.is_onleave,
            "is_laidoff": user.is_laidoff,
            "is_emergency": user.is_emergency,
            "is_supervisor": user.is_supervisor,
            "is_admin": user.is_admin,
            "is_manager": user.is_manager,
            "date_joined": user.date_joined.isoformat()
        }

    @staticmethod
    def to_list(queryset) -> list:
        """Convert queryset to list of dictionaries."""
        return [StaffSerializer.to_dict(user) for user in queryset]

    @staticmethod
    def minimal(user: User) -> Dict[str, Any]:
        """Return minimal user information."""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "region": user.region
        }
