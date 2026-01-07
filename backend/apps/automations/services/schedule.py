from datetime import datetime, date
from collections import defaultdict
from django.db import transaction
from models import Task, Clients, WeeklySchedule
from utils.date_helper import get_date_from_string_or_obj


@transaction.atomic
def routes():
    """
    Generate weekly schedules by grouping clients based on their latest service dates.

    Creates WeeklySchedule entries organized by:
    - Region → Weekday → Route → Client assignments
    """
    try:
        tasks = Task.objects.all()
        clients = Clients.objects.all()

        # Build map of latest service dates per client
        client_latest_service_dates = {}
        for task in tasks:
            client_name = getattr(task, 'client_assigned', None)
            task_service_date_val = getattr(task, 'due_date', None)

            if not client_name or not task_service_date_val:
                continue

            current_task_date_obj = get_date_from_string_or_obj(task_service_date_val)
            if not current_task_date_obj:
                print(f"Warning: Invalid date for task {getattr(task, 'id', 'N/A')}")
                continue

            # Track latest service date
            if client_name not in client_latest_service_dates or \
               current_task_date_obj > client_latest_service_dates[client_name]:
                client_latest_service_dates[client_name] = current_task_date_obj

        # Structure: {'Region': {'Weekday': {'RouteName': [{'client_name': 'X', 'service_date': date_obj}]}}}
        regional_weekday_route_schedule_data = {}

        for client in clients:
            company_name = getattr(client, 'company_name', None)
            client_main_region = getattr(client, 'region', None)
            route_name = getattr(client, 'branch_asoc', None)

            if not all([company_name, client_main_region, route_name]):
                print(f"Warning: Client {getattr(client, 'id', 'N/A')} missing required fields")
                continue

            service_date_for_client = client_latest_service_dates.get(company_name)
            if not service_date_for_client:
                continue

            weekday_name = service_date_for_client.strftime('%A')

            # Build nested structure
            regional_weekday_route_schedule_data \
                .setdefault(client_main_region, {}) \
                .setdefault(weekday_name, {}) \
                .setdefault(route_name, []) \
                .append({
                    'client_name': company_name,
                    'service_date': service_date_for_client
                })

        # Bulk create schedules (avoiding duplicates)
        schedules_to_create = []

        for region_name, weekdays_data in regional_weekday_route_schedule_data.items():
            for weekday, routes_data in weekdays_data.items():
                for route, client_details_list in routes_data.items():
                    for client_detail in client_details_list:
                        client_name = client_detail['client_name']
                        service_date = client_detail['service_date']

                        # Check for existing entry
                        if not WeeklySchedule.objects.filter(
                            region=region_name,
                            weekday=weekday,
                            route=route,
                            client_name=client_name,
                            date_to_service=service_date
                        ).exists():
                            schedules_to_create.append(
                                WeeklySchedule(
                                    region=region_name,
                                    weekday=weekday,
                                    route=route,
                                    client_name=client_name,
                                    date_to_service=service_date
                                )
                            )

        # Save to database
        if schedules_to_create:
            try:
                WeeklySchedule.objects.bulk_create(schedules_to_create, ignore_conflicts=True)
                print(f"Successfully saved {len(schedules_to_create)} weekly schedule entries.")
            except Exception as db_error:
                print(f"Error during bulk_create: {db_error}")
        else:
            print("No new schedule entries to save.")

    except Exception as e:
        import traceback
        print(f"An error occurred in routes(): {e}")
        traceback.print_exc()
