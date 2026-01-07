"""
URL patterns for branch management views.
"""
from django.urls import path
from automations.views import branch

urlpatterns = [
    path('', branch.show_branches, name='show_branches'),
    path('add/', branch.add_branch, name='add_branch'),
    path('upload/', branch.upload_branch_file, name='upload_branch_file'),
    path('<int:branch_id>/edit/', branch.edit_branch, name='edit_branch'),
    path('delete/', branch.delete_branch, name='delete_branch'),
]

