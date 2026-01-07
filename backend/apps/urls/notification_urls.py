"""
URL patterns for notification views.
"""
from django.urls import path
from automations.views import notifications

urlpatterns = [
    path('', notifications.notifications, name='notifications_list'),
    path('<int:notification_id>/read/', notifications.mark_notification_read, name='mark_notification_read'),
    path('read-all/', notifications.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('<int:notification_id>/delete/', notifications.delete_notification, name='delete_notification'),
    path('bulk-send/', notifications.send_bulk_notification, name='send_bulk_notification'),
]

