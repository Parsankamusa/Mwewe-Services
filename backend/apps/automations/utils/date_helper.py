from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from  automations.models import FrequencySettings
from datetime import datetime, date
from typing import Optional, Union

def get_date_from_string_or_obj(date_input):
    """Convert various date formats to date object."""
    if not date_input:
        return None
    try:
        if isinstance(date_input, str):
            return datetime.strptime(date_input, '%Y-%m-%d').date()
        if isinstance(date_input, datetime):
            return date_input.date()
        if isinstance(date_input, date):
            return date_input
    except (ValueError, TypeError):
        return None
    return None


def day(date_str):
    """Get day of week from date string."""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%A")


def calculate_next_due_date(base_date, frequency):
    """Calculate next service date based on frequency."""


    frequency_lower = str(frequency).lower()

    try:
        freq_setting = FrequencySettings.objects.get(
            frequency_name=frequency_lower,
            is_active=True
        )
        delta_days = freq_setting.interval_days
    except FrequencySettings.DoesNotExist:
        frequency_fallback = {
            "weekly": 7,
            "bi-monthly": 14,
            "bi-weekly": 4,
            "tri-monthly": 10,
            "monthly": 28
        }
        delta_days = frequency_fallback.get(frequency_lower)
        if not delta_days:
            return None

    today = datetime.today().date()
    next_due_date = base_date
    delta = timedelta(days=delta_days)

    while next_due_date < today:
        next_due_date += delta

    return next_due_date


def parse_date(date_input: Union[str, datetime, date, None], default=None) -> Optional[date]:
    """
    Parse various date formats to date object.

    Args:
        date_input: String, datetime, or date object
        default: Default value if parsing fails

    Returns:
        date object or default value
    """
    if not date_input:
        return default

    if isinstance(date_input, date):
        return date_input

    if isinstance(date_input, datetime):
        return date_input.date()

    # Try parsing string formats
    date_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y"
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(str(date_input).strip(), fmt).date()
        except ValueError:
            continue

    return default
