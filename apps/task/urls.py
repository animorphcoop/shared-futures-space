from typing import List, Union

from django.urls import URLResolver, URLPattern, path

from task.views import TaskView

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path("", TaskView.as_view(), name="tasks"),
]