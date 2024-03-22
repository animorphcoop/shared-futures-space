from typing import List, Union

from django.contrib.auth.decorators import login_required
from django.urls import URLPattern, URLResolver, path
from task.views import (
    CreateTaskView,
    DeleteTaskView,
    EditDoneTaskView,
    EditTaskView,
    ListTaskView,
)

from .views import (
    ActView,
    CreateRiverPollView,
    EditRiverView,
    EnvisionView,
    ManageRiverView,
    PlanView,
    ReflectView,
    RiverChatMessageListView,
    RiverChatUpdateView,
    RiverChatView,
    RiverStartWizardView,
    RiverView,
)

# !!! when adding new urls, don't forget to make them login_required if appropriate!
urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path(
        "create/",
        login_required(RiverStartWizardView.as_view()),
        name="start_river",
    ),
    path(
        "view/<str:slug>/",
        RiverView.as_view(),
        name="view_river",
    ),
    path(
        "view/<str:slug>/envision/",
        EnvisionView.as_view(),
        name="view_envision",
    ),
    path(
        "view/<str:slug>/plan/",
        PlanView.as_view(),
        name="view_plan",
    ),
    path(
        "view/<str:slug>/act/",
        ActView.as_view(),
        name="view_act",
    ),
    path(
        "view/<str:slug>/reflect/",
        ReflectView.as_view(),
        name="view_reflect",
    ),
    path(
        "view/<str:slug>/createpoll/<str:stage>/<str:topic>/",
        CreateRiverPollView.as_view(),
        name="create_river_poll",
    ),
    path(
        "view/<str:slug>/chat/<str:stage>/<str:topic>/",
        RiverChatView.as_view(template_name="river_chat.html"),
        name="river_chat",
    ),
    path(
        "view/<str:slug>/chat/<str:stage>/<str:topic>/count/",
        RiverChatUpdateView.as_view(),
        name="river_chat_message_count",
    ),
    path(
        "view/<str:slug>/chat/<str:stage>/<str:topic>/message_list/",
        RiverChatMessageListView.as_view(template_name="messaging/message_list.html"),
        name="river_chat_message_list",
    ),
    path(
        "edit/<str:slug>/",
        login_required(EditRiverView.as_view(template_name="edit_river.html")),
        name="edit_river",
    ),
    path(
        "manage/<str:slug>/",
        ManageRiverView.as_view(template_name="swimmers_list.html"),
        name="manage_river",
    ),
    # Tasks
    # nested inside river+stage+topic
    path(
        "view/<str:slug>/task/<str:stage>/<str:topic>/",
        ListTaskView.as_view(),
        name="river_task_list",
    ),
    path(
        "view/<str:slug>/task/<str:stage>/<str:topic>/add/",
        login_required(CreateTaskView.as_view()),
        name="river_task_add",
    ),
    path(
        "view/<str:slug>/task/<str:stage>/<str:topic>/edit/<str:uuid>/",
        EditTaskView.as_view(),
        name="river_task_edit",
    ),
    path(
        "view/<str:slug>/task/<str:stage>/<str:topic>/done/<str:uuid>/",
        EditDoneTaskView.as_view(),
        name="river_task_edit_done",
    ),
    path(
        "view/<str:slug>/task/<str:stage>/<str:topic>/delete/<str:uuid>",
        DeleteTaskView.as_view(),
        name="river_task_delete",
    ),
    # path('change/title/<str:slug>/', ManageRiverView.as_view(template_name='swimmers_list.html'), name='manage_river'),
]
