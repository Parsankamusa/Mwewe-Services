from datetime import datetime, timedelta
from collections import defaultdict
from django.db import transaction
from models import Workload, VehicleRoute, Vehicles, Clients, SubRegion


class VehicleAssigner:
    """
    Assigns specialized vehicles to sub-regions based on client service requirements.

    Strategies:
    1. Single multi-service vehicle (if available)
    2. Team assembly of specialist vehicles
    3. Mark as unassigned if no solution found
    """

    def __init__(self):
        self.service_date = datetime.today().date() + timedelta(days=1)

        # Data structures
        self.assignments_by_subregion = defaultdict(lambda: defaultdict(list))
        self.vehicles_by_region = defaultdict(list)
        self.vehicle_specs = {}

        # Results tracking
        self.final_summary_assigned = defaultdict(lambda: {
            'region': '',
            'sub_regions': set()
        })
        self.final_summary_unassigned = []

    def run(self):
        """Main execution pipeline."""
        print(f"\n{'='*60}")
        print(f"  Vehicle Assignment for: {self.service_date.strftime('%Y-%m-%d, %A')}")
        print(f"{'='*60}\n")

        self._group_assignments_by_location()

        if not self.assignments_by_subregion:
            print("INFO: No client assignments found. Skipping vehicle assignment.")
            return {}

        self._load_vehicles()
        self._process_assignments()
        self._generate_report()

        return dict(self.final_summary_assigned)

    def _group_assignments_by_location(self):
        """Group assigned clients by region and sub-region."""
        workloads = Workload.objects.filter(date_assigned=self.service_date)

        if not workloads.exists():
            return

        # Get client locations
        client_names = workloads.values_list('client_assigned', flat=True)
        client_locations = {
            client.company_name: (client.region, client.branch_asoc)
            for client in Clients.objects.filter(company_name__in=client_names)
        }

        # Build route → sub-region mapping
        route_to_subregion_map = {}
        for sub in SubRegion.objects.all():
            routes_str = getattr(sub, 'routes_in_sub_region', '')
            for route in routes_str.split(','):
                route_to_subregion_map[route.strip().lower()] = sub.name.strip().lower()

        # Group clients
        for item in workloads:
            client_name = item.client_assigned
            location = client_locations.get(client_name)

            if not location:
                continue

            region, route = location
            region = region.strip().lower()
            route = route.strip().lower()

            sub_region = route_to_subregion_map.get(route, 'unmapped_routes')
            self.assignments_by_subregion[region][sub_region].append(client_name)

    def _load_vehicles(self):
        """Load available vehicles and cache their capabilities."""
        for vehicle in Vehicles.objects.filter(is_available=True):
            region = vehicle.region.strip().lower()
            self.vehicles_by_region[region].append(vehicle)

            self.vehicle_specs[vehicle.vehicle_name] = {
                'can_handle_all': vehicle.can_handle_all_services,
                'specs': set(s.strip().lower() for s in vehicle.specialization.split(',') if s.strip())
            }

    def _get_required_services_for_subregion(self, client_names):
        """Extract unique services.py required by a group of clients."""
        required_services = set()
        clients = Clients.objects.filter(company_name__in=client_names)

        for client in clients:
            services_str = getattr(client, 'services_required', '')
            if services_str:
                required_services.update(s.strip().lower() for s in services_str.split(',') if s.strip())

        return required_services

    def _find_vehicle_for_service_set(self, available_vehicles, required_services):
        """Find a single vehicle capable of handling all required services.py."""
        for vehicle in available_vehicles:
            specs = self.vehicle_specs[vehicle.vehicle_name]

            is_compatible = (
                specs['can_handle_all'] or
                required_services.issubset(specs['specs'])
            )

            if is_compatible:
                return vehicle

        return None

    def _assemble_vehicle_team(self, available_vehicles, required_services):
        """Create a team of specialist vehicles to cover all services.py."""
        uncovered_services = set(required_services)
        team = []

        for vehicle in available_vehicles:
            if not uncovered_services:
                break

            specs = self.vehicle_specs[vehicle.vehicle_name]

            if specs['can_handle_all']:
                return [vehicle]

            services_this_vehicle_can_cover = uncovered_services & specs['specs']

            if services_this_vehicle_can_cover:
                team.append(vehicle)
                uncovered_services -= services_this_vehicle_can_cover

        if uncovered_services:
            return None

        return team

    @transaction.atomic
    def _process_assignments(self):
        """Assign vehicles to sub-regions using multi-strategy approach."""
        for region, sub_regions_data in self.assignments_by_subregion.items():
            print(f"\nProcessing Region: {region.title()}")
            vehicles_in_region = self.vehicles_by_region.get(region, [])

            # Sort by client count (descending)
            sorted_sub_regions = sorted(
                sub_regions_data.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )

            print(f"  {len(sorted_sub_regions)} sub-region(s) | "
                  f"{len(vehicles_in_region)} vehicle(s) available")

            for sub_region_name, client_list in sorted_sub_regions:
                print(f"\n  Sub-Region: {sub_region_name.title()} ({len(client_list)} clients)")

                required_services = self._get_required_services_for_subregion(client_list)
                print(f"    Required Services: {sorted(required_services)}")

                # Strategy 1: Single Vehicle
                single_vehicle = self._find_vehicle_for_service_set(vehicles_in_region, required_services)

                if single_vehicle:
                    assignment_map = {client: single_vehicle.vehicle_name for client in client_list}
                    self._save_assignments(assignment_map, client_list)

                    self.final_summary_assigned[single_vehicle.vehicle_name]['region'] = region
                    self.final_summary_assigned[single_vehicle.vehicle_name]['sub_regions'].add(sub_region_name)

                    print(f"     ✓ Assigned single vehicle: {single_vehicle.vehicle_name}")
                    continue

                # Strategy 2: Vehicle Team
                team = self._assemble_vehicle_team(vehicles_in_region, required_services)

                if team:
                    assignment_map = {}
                    for client in client_list:
                        for vehicle in team:
                            client_obj = Clients.objects.filter(company_name=client).first()
                            if not client_obj:
                                continue

                            client_services = set(s.strip().lower() for s in client_obj.services_required.split(','))
                            vehicle_specs = self.vehicle_specs[vehicle.vehicle_name]

                            if vehicle_specs['can_handle_all'] or client_services.issubset(vehicle_specs['specs']):
                                assignment_map[client] = vehicle.vehicle_name
                                break

                    self._save_assignments(assignment_map, client_list)

                    for vehicle in team:
                        self.final_summary_assigned[vehicle.vehicle_name]['region'] = region
                        self.final_summary_assigned[vehicle.vehicle_name]['sub_regions'].add(sub_region_name)

                    print(f"     ✓ Assigned vehicle team: {[v.vehicle_name for v in team]}")
                    continue

                # Strategy 3: Mark as Unassigned
                print(f"     ✗ No compatible vehicle/team found")
                self.final_summary_unassigned.append({
                    'region': region,
                    'sub_region': sub_region_name,
                    'clients': client_list,
                    'required_services': sorted(required_services)
                })

    def _save_assignments(self, assignment_map, client_list):
        """Persist vehicle assignments to database."""
        for client_name, vehicle_name in assignment_map.items():
            client_obj = Clients.objects.filter(company_name=client_name).first()

            if not client_obj:
                continue

            VehicleRoute.objects.update_or_create(
                client_name=client_name,
                defaults={
                    'vehicle_name': vehicle_name,
                    'date_assigned': self.service_date
                }
            )

        print(f"     → Saved {len(client_list)} assignments to database")

    def _generate_report(self):
        """Print summary of vehicle assignments."""
        print(f"\n{'='*60}")
        print("           VEHICLE ASSIGNMENT SUMMARY")
        print(f"{'='*60}\n")

        if self.final_summary_assigned:
            print("[+] Assigned Vehicles:")
            for vehicle, details in self.final_summary_assigned.items():
                print(f"  {vehicle} → Region: {details['region'].title()} | "
                      f"Sub-Regions: {', '.join(sorted(details['sub_regions']))}")
        else:
            print("No vehicles were assigned.")

        if self.final_summary_unassigned:
            print("\n[-] Unassigned Sub-Regions:")
            for details in self.final_summary_unassigned:
                print(f"  Region: {details['region'].title()} | "
                      f"Sub-Region: {details['sub_region'].title()} | "
                      f"Clients: {len(details['clients'])} | "
                      f"Missing Services: {details['required_services']}")

        print(f"\n{'='*60}\n")


def vehicle_enroute():
    """Entry point for vehicle assignment."""
    assigner = VehicleAssigner()
    return assigner.run()
