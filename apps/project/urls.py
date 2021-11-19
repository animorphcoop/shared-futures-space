# pyre-strict

from django.urls import path, URLResolver, URLPattern
from .views import AllProjectsView, ProjectView, MakeProjectView, EditProjectView, DeleteMessageView
from typing import List, Union


urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('', AllProjectsView.as_view(template_name='all_projects.html'), name='all_projects'),
    path('view/<int:pk>/', ProjectView.as_view(template_name='project.html'), name='view_project'),
    path('new/', MakeProjectView.as_view(template_name='new_project.html'), name='new_project'),
    path('edit/<int:pk>/', EditProjectView.as_view(template_name='edit_project.html'), name='edit_project'),
    path('deletemessage/', DeleteMessageView.as_view(), name='delete_message'),
]
