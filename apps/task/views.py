from typing import Any, Dict, List, Union

from django.contrib.auth.decorators import login_required
from django.db.models.expressions import F
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import ContextMixin, TemplateView, View
from django.views.generic.edit import CreateView
from river.models import River
from task.models import Task


class TaskViewMixin(ContextMixin, View):
    def get_slug(self) -> str:
        return self.kwargs["slug"]

    def get_stage_name(self) -> str:
        return self.kwargs["stage"]

    def get_topic(self) -> str:
        return self.kwargs["topic"]

    def get_river(self) -> River:
        river = River.objects.get(slug=self.get_slug())
        return river

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            dict(
                slug=self.get_slug(),
                stage=self.get_stage_name(),
                topic=self.get_topic(),
            )
        )
        return context


class TaskListView(TaskViewMixin, TemplateView):
    template_name = "task/tasks.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        river = River.objects.get(slug=self.kwargs["slug"])
        tasks = river.task_set.filter(stage_name=self.kwargs["stage"]).order_by(
            F("due").asc(nulls_last=True)
        )
        context.update(
            dict(
                river=river,
                tasks=tasks,
            )
        )
        return context


# class RiverTaskEditView(TemplateView):
#     def get(self, request: HttpRequest, *args, **kwargs):
#         raise Exception("NOT REALLY IMPLEMENTED YET")
#         if not request.htmx:
#             raise Exception('must be an htmx request')
#
#         context = {}
#         return render(request, "task/partials/task_edit.html")


class TaskCreateView(TaskViewMixin, CreateView):
    model = Task
    # form_class = CreateTaskForm
    fields = ["name", "due", "responsible"]
    template_name = "task/partials/task_edit.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        slug = self.get_slug()
        stage_name = self.get_stage_name()
        topic = self.get_topic()

        context = super().get_context_data(**kwargs)
        river = self.get_river()
        member = river.rivermembership_set.get(user=self.request.user)
        if member.starter:
            members = river.rivermembership_set.all()
        else:
            members = [member]
        context.update(
            dict(
                river=river,
                member=member,
                members=members,
            )
        )
        return context

    def get_success_url(self) -> str:
        # TODO: when completing this request, probably need to take over the full response, so redirect for full page, htmx directly renders the partial
        if self.request.htmx:
            return reverse(
                "river_task_list",
                args=[self.get_slug(), self.get_stage_name(), self.get_topic()],
            )
        return reverse(
            "river_chat",
            args=[self.get_slug(), self.get_stage_name(), self.get_topic()],
        )

    def form_valid(self, form) -> HttpResponse:
        form.instance.river = self.get_river()
        form.instance.stage_name = self.get_stage_name()
        form.instance.topic = self.get_topic()
        return super().form_valid(form)

    def form_invalid(self, form) -> HttpResponse:
        # TODO: there might be things we don't handle here very well...
        print("FORM INVALID")
        return super().form_invalid(form)
