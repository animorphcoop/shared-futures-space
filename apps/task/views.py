from typing import List, Any, Dict, Union

from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import TemplateView


class TaskView(TemplateView):
    def get(
            self, request: HttpRequest, *args: List[Any], **kwargs: Dict[str, str]
    ) -> Union[HttpResponse, HttpResponseRedirect]:
        context = {}
        return render(request, "task/tasks.html", context)


class RiverTaskListView(TemplateView):
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        print('rendering river task list view')
        return render(request, "task/task_list.html", context)