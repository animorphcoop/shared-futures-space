from typing import Any, Dict, List, Union

from core.views import HTMXMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import models
from django.db.models.expressions import F
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic.base import ContextMixin, TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from river.models import River, RiverMembership
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
        return self.get_membership().river

    def get_membership(self) -> RiverMembership:
        return RiverMembership.objects.get(
            river__slug=self.get_slug(),
            user=self.request.user,
        )

    def get_members(self):
        """Members for the river, taking into consideration current user permissions"""
        membership = self.get_membership()
        river = membership.river
        members = [membership]
        if membership.starter:
            members += river.rivermembership_set.exclude(
                user=self.request.user
            ).order_by("user__display_name")
        return members

    def get_queryset(self):
        """A queryset that is filtered river/stage/topic/memberships"""
        return (
            super()
            .get_queryset()
            .filter(
                river__rivermembership__user=self.request.user,
                river__slug=self.get_slug(),
                stage_name=self.get_stage_name(),
                topic=self.get_topic(),
            )
        )

    def get_object(self):
        """Access an individual task

        Depends on river permissions:
        - river "starters" can access everyone's
        - everyone else can only access the ones they are responsible for
        """
        queryset = self.get_queryset()
        membership = self.get_membership()
        if not membership.starter:
            queryset = queryset.filter(responsible=self.request.user)
        return get_object_or_404(queryset, uuid=self.kwargs["uuid"])

    def get_success_url(self) -> str:
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


class EditTaskView(LoginRequiredMixin, TaskViewMixin, UpdateView):
    model = Task
    fields = ["name", "due", "responsible"]
    template_name = "task/task_edit.html"
    template_name_htmx = "task/partials/task_edit.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["members"] = self.get_members()
        return context


class EditDoneTaskView(LoginRequiredMixin, TaskViewMixin, UpdateView):
    """View just for modifying the done state"""

    model = Task
    fields = ["done"]

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """POST-only There is no template for this, so just redirect on get requests"""
        return redirect(self.get_success_url())


class DeleteTaskView(LoginRequiredMixin, TaskViewMixin, DeleteView):
    model = Task
    template_name_htmx = "task/partials/task_delete.html"
