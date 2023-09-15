from typing import Any, Dict, List, Union

from core.views import HTMXMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models.expressions import F
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.base import ContextMixin, TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from river.models import River
from task.models import Task


class TaskViewMixin(HTMXMixin, ContextMixin, View):
    """Various things common across the Task views"""

    def get_slug(self) -> str:
        return self.kwargs["slug"]

    def get_stage_name(self) -> str:
        return self.kwargs["stage"]

    def get_topic(self) -> str:
        return self.kwargs["topic"]

    def get_river(self) -> River:
        return River.objects.get(slug=self.get_slug())

    def get_members(self):
        """Members for the river, taking into consideration current user permissions"""
        river = self.get_river()
        member = river.rivermembership_set.get(user=self.request.user)
        members = [member]
        if member.starter:
            members += river.rivermembership_set.exclude(
                user=self.request.user
            ).order_by("user__display_name")
        return members

    def get_queryset(self):
        """A queryset that is filtered by slug and stage route params"""
        return (
            super()
            .get_queryset()
            .filter(
                river__slug=self.get_slug(),
                stage_name=self.get_stage_name(),
                topic=self.get_topic(),
            )
        )

    def get_success_url(self) -> str:
        # TODO: when completing this request, probably need to take over the full response, so redirect for full page, htmx directly renders the partial
        if self.request.htmx:
            return reverse(
                "river_task_list",
                args=[self.get_slug(), self.get_stage_name(), self.get_topic()],
            )
        # for non-htmx requests we can't actually send them to the correct place
        # so do the next best thing we can find :/
        return reverse(
            "view_river",
            args=[self.get_slug()],
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["slug"] = self.get_slug()
        context["stage"] = self.get_stage_name()
        context["topic"] = self.get_topic()
        return context


class ListTaskView(LoginRequiredMixin, TaskViewMixin, ListView):
    model = Task
    template_name = "task/tasks.html"
    template_name_htmx = "task/partials/task_list.html"
    paginate_by = 1000  # show all, as no pagination in template (yet)
    ordering = [
        F("due").asc(nulls_last=True),
        F("created_at").asc(),
    ]


class CreateTaskView(LoginRequiredMixin, TaskViewMixin, CreateView):
    model = Task
    fields = ["name", "due", "responsible"]
    template_name = "task/task_edit.html"
    template_name_htmx = "task/partials/task_edit.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["members"] = self.get_members()
        return context

    def form_valid(self, form) -> HttpResponse:
        form.instance.river = self.get_river()
        form.instance.stage_name = self.get_stage_name()
        form.instance.topic = self.get_topic()
        return super().form_valid(form)

    def form_invalid(self, form) -> HttpResponse:
        # TODO: there might be things we don't handle here very well...
        print("FORM INVALID")
        return super().form_invalid(form)


class EditTaskView(LoginRequiredMixin, TaskViewMixin, UpdateView):
    model = Task
    fields = ["name", "due", "responsible"]
    template_name = "task/task_edit.html"
    template_name_htmx = "task/partials/task_edit.html"

    def get_object(self):
        return self.get_queryset().get(uuid=self.kwargs["uuid"])

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["members"] = self.get_members()
        return context


class EditDoneTaskView(LoginRequiredMixin, TaskViewMixin, UpdateView):
    """View just for modifying the done state"""

    model = Task
    fields = ["done"]

    def get_object(self):
        return self.get_queryset().get(uuid=self.kwargs["uuid"])

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """There is no template for this, so just redirect on get requests"""
        return redirect(self.get_success_url())


class DeleteTaskView(LoginRequiredMixin, TaskViewMixin, DeleteView):
    model = Task

    template_name_htmx = "task/partials/task_delete.html"

    def get_object(self):
        return self.get_queryset().get(uuid=self.kwargs["uuid"])
