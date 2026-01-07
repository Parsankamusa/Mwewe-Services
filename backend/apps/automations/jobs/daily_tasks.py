from django.db import transaction
from admindash.services.autotask.assigner import AutoTaskAssigner
from admindash.services.scheduling import routes
from admindash.services.vehicles import vehicle_enroute
from admindash.services.task_manager import (
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
