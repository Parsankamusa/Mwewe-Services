"""
URL patterns for vehicle route views.
"""
from django.urls import path
from automations.views import routes_views

urlpatterns = [
    path('', routes_views.show_routes, name='show_routes'),
    path('<int:route_id>/edit/', routes_views.edit_route, name='edit_route'),
    path('delete/', routes_views.delete_route, name='delete_route'),
]

