from datetime import datetime, timedelta
from collections import defaultdict
import random
from django.db import transaction

from automations.models import (
    Clients, User, Task, Workload, SubRegion,
    SharedLocations, StaffAssignmentResult
)
from services.task_managers import send_staff_assignment_notification
from utils.date_helper import get_date_from_string_or_obj, calculate_next_due_date

REGION_PRIORITY = ["Eastern", "Coast", "Western", "North Western", "Nairobi"]


class AutoTaskAssigner:
    """
    Main class for automated task assignment.
    Handles staff allocation, client distribution, and workload balancing.
    """

    def __init__(self):
        self.today_date = datetime.today().date()
        self.service_date_target = self.today_date + timedelta(days=1)

        # Data containers
        self.clients_to_be_assigned = []
        self.unassigned_clients_log = []

        # Organizational structures
        self.region_sub_region_to_locations_due = defaultdict(
            lambda: defaultdict(lambda: defaultdict(list))
        )
        self.region_to_staff = defaultdict(list)
        self.staff_to_regions = defaultdict(list)
        self.staff_workloads = defaultdict(int)
        self.final_assignments = defaultdict(list)

        # Staff management
        self.staff_sub_region_assignments = {}
        self.multi_region_staff = set()
        self.staff_specializations = {}
        self.staff_in_pools = set()
        self.region_to_considered_staff = defaultdict(set)

        # Access control
        self.special_access_rules = defaultdict(set)
        self.special_access_clients = defaultdict(set)
        self.subregion_allowed_staff = defaultdict(list)
        self.all_subregion_restricted_staff = set()

        # Location management
        self.client_name_to_location = {}
        self.staff_location_group_lock = {}

    def run(self):
        """Main execution method."""
        print(f"--- Running Autotask on {self.today_date} for services due on {self.service_date_target} ---")

        try:
            if not self._perform_pre_checks():
                return

            self._fetch_and_filter_due_clients()
            self._prepare_special_access_data()
            self._load_specialization_data()
            self._load_subregion_staff_rules()
            self._identify_special_clients_from_rules()
            self._group_clients_by_location()
            self._prepare_staff_data()
            self._process_assignments()
            self._generate_report()
            self._run_post_processes()

        except Exception as e:
            print(f"CRITICAL ERROR in AutoTaskAssigner: {e}")
            import traceback
            traceback.print_exc()

    # ... (rest of the methods from your original class)
