from django.contrib.auth import get_user_model
import re
from typing import Tuple, Optional

User = get_user_model()


class StaffValidationError(Exception):
    """Custom exception for staff validation failures."""
    pass


def validate_staff_availability(username):
    """
    Validate staff member can receive assignments.

    Raises:
        StaffValidationError: If staff cannot be assigned work
    """
    try:
        staff_member = User.objects.get(username=username)

        if not staff_member.is_active:
            raise StaffValidationError(
                f"Staff member '{username}' is inactive"
            )

        if staff_member.is_onleave:
            raise StaffValidationError(
                f"Staff member '{username}' is on leave"
            )

        if staff_member.is_laidoff:
            raise StaffValidationError(
                f"Staff member '{username}' is laid off"
            )

        if staff_member.is_emergency:
            raise StaffValidationError(
                f"Staff member '{username}' is in emergency status"
            )

        return staff_member

    except User.DoesNotExist:
        raise StaffValidationError(
            f"Staff member '{username}' does not exist"
        )



def validate_required_fields(data: dict, required_fields: list) -> Tuple[bool, Optional[str]]:
    """Validate that required fields are present in the data."""
    missing_fields = [field for field in required_fields if not data.get(field)]

    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    return True, None


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.fullmatch(email_regex, email))


def is_valid_phone(phone: str) -> bool:
    """
    Validate phone number format (Kenyan format).
    Accepts: 0712345678, 0112345678
    """
    phone_regex = r"^(07|01)\d{8}$"
    return bool(re.match(phone_regex, phone))
