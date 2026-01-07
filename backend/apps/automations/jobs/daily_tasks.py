from django.db import transaction
from services.auto_tasks.assigner import AutoTaskAssigner
from services.schedule import routes
from services.vehicle import vehicle_enroute
from services.task_managers import (
    filter_task,
    supervisor_data,
    send_client_reminder,
    pre_calculate_unassigned_clients
)


@transaction.atomic
def run_autotask_job():
    """
    Main scheduled job for daily task assignment.
    Runs all auto-assignment processes in sequence.
    """
    print("Starting the auto-task assignment process...\n")

    assigner = AutoTaskAssigner()
    assigner.run()

    pre_calculate_unassigned_clients()
    filter_task()
    # supervisor_data()  # Uncomment when ready
