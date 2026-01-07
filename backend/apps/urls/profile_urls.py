"""
URL patterns for user profile views.
"""
from django.urls import path
from automations.views import profile

urlpatterns = [
    path('', profile.profile, name='profile'),
    path('update/', profile.update_profile, name='update_profile'),
    path('change-password/', profile.change_password, name='change_password'),
]

