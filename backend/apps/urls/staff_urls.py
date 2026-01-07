"""
URL patterns for staff management views.
"""
from django.urls import path
from automations.views import staffs

urlpatterns = [
    path('', staffs.show_staff, name='show_staff'),
    path('register/', staffs.register_staff, name='register_staff'),
    path('edit/', staffs.edit_staff, name='edit_staff'),
    path('delete/', staffs.delete_staff, name='delete_staff'),
    path('upload/', staffs.upload_staff_file, name='upload_staff_file'),
]

