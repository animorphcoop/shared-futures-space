from django.urls import include, path, URLResolver, URLPattern
from django.contrib.auth.decorators import login_required
from .views import invoke_action_view

from typing import List, Union

# !!! when adding new urls, don't forget to make them login_required if appropriate!
urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('', login_required(invoke_action_view), name='do_action'),
]
