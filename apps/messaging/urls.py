# pyre-strict
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

from typing import List, Union
from django.urls import URLResolver, URLPattern

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('<str:user_path>/', login_required(views.paginated_messages), name='previous_messages'),  # pyre-ignore[16]


]
