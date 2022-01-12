# pyre-strict

from django.urls import path, URLResolver, URLPattern
from .views import AllIdeasView, IdeaView, MakeIdeaView, EditIdeaView, AllProjectsView, ProjectView, EditProjectView, ManageProjectView
from django.contrib.auth.decorators import login_required
from typing import List, Union


# !!! when adding new urls, don't forget to make them login_required if appropriate!
urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('ideas/', AllIdeasView.as_view(template_name='all_ideas.html'), name='all_ideas'),
    path('ideas/view/<int:pk>/', IdeaView.as_view(template_name='idea.html'), name='view_idea'),
    path('ideas/new/', login_required(MakeIdeaView.as_view(template_name='new_idea.html')), name='new_idea'),
    path('ideas/edit/<int:pk>/', login_required(EditIdeaView.as_view(template_name='edit_idea.html')), name='edit_idea'),
    path('projects/', AllProjectsView.as_view(template_name='all_projects.html'), name='all_projects'),
    path('projects/view/<int:pk>/', ProjectView.as_view(template_name='project.html'), name='view_project'),
    path('projects/edit/<int:pk>/', login_required(EditProjectView.as_view(template_name='edit_project.html')), name='edit_project'),
    path('projects/manage/<int:pk>/', login_required(ManageProjectView.as_view(template_name='manage_project.html')), name='manage_project'),
]
