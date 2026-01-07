"""
URL patterns for report views.
"""
from django.urls import path
from automations.views import reports

urlpatterns = [
    path('contracts/', reports.active_contracts_report, name='active_contracts_report'),
    path('tasks/', reports.task_report, name='task_report'),
]

