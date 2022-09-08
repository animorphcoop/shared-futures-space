# pyre-strict

from django.urls import path, URLResolver, URLPattern
from .views import AllProjectsView, ProjectView, EditProjectView, ManageProjectView, EnvisionView, PlanView, ActView, ReflectView
from django.contrib.auth.decorators import login_required
from typing import List, Union


# !!! when adding new urls, don't forget to make them login_required if appropriate!
urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('projects/', AllProjectsView.as_view(template_name='all_projects.html'), name='all_projects'),
    path('projects/view/<str:slug>/', ProjectView.as_view(template_name='project.html'), name='view_project'),
    path('projects/view/<str:slug>/envision/', EnvisionView.as_view(template_name='envision_view.html'), name='view_envision'),
    path('projects/view/<str:slug>/plan/',PlanView.as_view(template_name='plan_view.html'), name='view_plan'),
    path('projects/view/<str:slug>/act/', ActView.as_view(template_name='act_view.html'), name='view_act'),
    path('projects/view/<str:slug>/reflect/', ReflectView.as_view(template_name='reflect_view.html'), name='view_reflect'),
    path('projects/edit/<str:slug>/', login_required(EditProjectView.as_view(template_name='edit_project.html')), name='edit_project'),
    path('projects/manage/<str:slug>/', login_required(ManageProjectView.as_view(template_name='manage_project.html')), name='manage_project'),
    # no more single chat per project
    #path('projects/chat/<str:slug>/', ProjectChatView.as_view(template_name='project_chat.html'), name='project_chat'),
]
