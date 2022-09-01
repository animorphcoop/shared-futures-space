# pyre-strict
from django.conf import settings
from django.urls import include, path, URLResolver, URLPattern
from .views import PollView, PollCreateView
from typing import List, Union
from uuid import UUID

# !!! when adding new urls, don't forget to make them login_required if appropriate!
urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('<uuid:uuid>/', PollView.as_view(template_name='poll/poll_view.html'), name='poll_view'),
    path('create/', PollCreateView.as_view(), name='poll_create'),
]
