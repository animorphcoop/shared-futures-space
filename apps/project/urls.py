# pyre-strict

from django.urls import path, URLResolver, URLPattern
from .views import SpringView, ProjectView, EditProjectView, ManageProjectView, EnvisionView, PlanView, ActView, ReflectView, ProjectChatView, ProjectStartView
from django.contrib.auth.decorators import login_required
from typing import List, Union


# !!! when adding new urls, don't forget to make them login_required if appropriate!
urlpatterns: List[Union[URLResolver, URLPattern]] = [
    #path('spring/<uuid:uuid>', SpringView.as_view(template_name='all_projects.html'), name='spring'),
    path('create/', ProjectStartView.as_view(template_name='start_project.html'), name='start_project'),
    path('view/<str:slug>/', ProjectView.as_view(template_name='project.html'), name='view_project'),
    path('view/<str:slug>/envision/', EnvisionView.as_view(template_name='envision_view.html'), name='view_envision'),
    path('view/<str:slug>/plan/',PlanView.as_view(template_name='plan_view.html'), name='view_plan'),
    path('view/<str:slug>/act/', ActView.as_view(template_name='act_view.html'), name='view_act'),
    path('view/<str:slug>/reflect/', ReflectView.as_view(template_name='reflect_view.html'), name='view_reflect'),
    path('view/<str:slug>/chat/<str:stage>/<str:topic>/', ProjectChatView.as_view(template_name = 'messaging/chatbox_snippet.html'), name = 'project_chat'), # pyre-ignore[16]
    path('edit/<str:slug>/', login_required(EditProjectView.as_view(template_name='edit_project.html')), name='edit_project'),
    path('manage/<str:slug>/', login_required(ManageProjectView.as_view(template_name='manage_project.html')), name='manage_project'),
    path('<str:slug>/', SpringView.as_view(template_name='all_projects.html'), name='spring'),

]
