from typing import Dict, Any
from automations.models.clients import Clients


class ClientSerializer:
    """Serialize client model instances."""

    @staticmethod
    def to_dict(client: Clients) -> Dict[str, Any]:
        """Convert client instance to dictionary."""
        return {
            "id": client.id,
            "company_name": client.company_name,
            "contract_id": client.contract_id,
            "region": client.region,
            "branch_asoc": client.branch_asoc,
            "services_required": client.services_required,
            "frequency": client.frequency,
            "premise_location": client.premise_location,
            "contact_phone": client.contact_phone,
            "email": client.email,
            "quantity": client.quantity,
            "contract_date": client.contract_date.isoformat() if client.contract_date else None,
            "renewal_date": client.renewal_date.isoformat() if client.renewal_date else None,
            "next_service_date": client.next_service_date.isoformat() if client.next_service_date else None,
            "is_active": client.is_active
        }

    @staticmethod
    def to_list(queryset) -> list:
        """Convert queryset to list of dictionaries."""
        return [ClientSerializer.to_dict(client) for client in queryset]
