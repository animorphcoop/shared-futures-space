# pyre-strict
from django.conf import settings
from django.urls import include, path, URLResolver, URLPattern
from .views import PollView
from typing import List, Union
from uuid import UUID

# !!! when adding new urls, don't forget to make them login_required if appropriate!
urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('<uuid:uuid>/', PollView, name='poll_view'), # pyre-ignore[16]
]
