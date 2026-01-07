"""
URL patterns for task management views.
"""
from django.urls import path
from automations.views import task

urlpatterns = [
    path('', task.show_tasks, name='show_tasks'),
    path('assign/', task.assign_task, name='assign_task'),
    path('<int:task_id>/edit/', task.edit_task, name='edit_task'),
    path('approval/', task.task_approval, name='task_approval'),
    path('delete/', task.delete_task, name='delete_task'),
]

