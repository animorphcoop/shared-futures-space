# pyre-strict

from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

from .models import Idea, IdeaSupport, Project, ProjectMembership, ProjectSupport
from typing import Dict, List, Any

class IdeaView(DetailView):
    model = Idea
    def post(self, request: WSGIRequest, pk: int) -> HttpResponse:
        if (request.POST['action'] == 'give_support'):
            # can't suppport one idea more than once
            if (0 == len(IdeaSupport.objects.filter(idea=Idea.objects.get(id=pk), # pyre-ignore[16]
                                                    user=request.user))): # pyre-ignore[16]
                support = IdeaSupport(idea=Idea.objects.get(id=pk),
                                      user=request.user)
                support.save()
                # TODO: is this the only place support can be given? if not, need to check elsewhere as well
                if (len(IdeaSupport.objects.filter(idea=Idea.objects.get(id=pk))) >= settings.PROJECT_REQUIRED_SUPPORTERS):
                    new_project_id = replace_idea_with_project(Idea.objects.get(id=pk))
                    return redirect(reverse('view_project', args=[new_project_id]))
        elif (request.POST['action'] == 'remove_support'):
            # can't remove support from your own idea (because you wouldn't be able to return it through the intended interface)
            if (request.user != Idea.objects.get(id=pk).proposed):
                supports = IdeaSupport.objects.filter(idea=Idea.objects.get(id=pk),
                                                      user=request.user)
                for support in supports: # there should only be one, but no need to assume that
                    support.delete()
        return super().get(request, pk)
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        context = super().get_context_data(**kwargs)
        context['supporters'] = IdeaSupport.objects.filter(idea=context['object'].pk) # pyre-ignore[16]
        return context

class AllIdeasView(TemplateView):
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        context = super().get_context_data(**kwargs)
        context['ideas'] = Idea.objects.all() # pyre-ignore[16]
        return context

class MakeIdeaView(TemplateView):
    def post(self, request: WSGIRequest, **kwargs: Dict[str,Any]) -> HttpResponse:
        new_idea = Idea(name=request.POST['name'], description=request.POST['description'], proposed=request.user) # pyre-ignore[16]
        new_idea.save()
        new_support = IdeaSupport(idea=new_idea, user=request.user)
        new_support.save()
        return redirect(reverse('all_ideas'))

class EditIdeaView(UpdateView):
    model = Idea
    fields = ['name', 'description']
    def get(self, *args: List[Any], **kwargs: Dict[str, Any]) -> HttpResponse:
        return login_required(super().get)(*args, **kwargs) # login_required is idempotent so we may as well apply it here in case it's forgotten in urls.py
    def post(self, request: WSGIRequest, pk: int, **kwargs: Dict[str,Any]) -> HttpResponse: # pyre-ignore[14]
        idea = Idea.objects.get(id=pk) # pyre-ignore[16]
        if request.POST['action'] == 'update':
            idea.name = request.POST['name']
            idea.description = request.POST['description']
            idea.save()
        elif request.POST['action'] == 'delete':
            idea.delete()
            return redirect(reverse('all_ideas'))
        return redirect(reverse('view_idea', args=[pk]))

# ---

def replace_idea_with_project(idea: Idea) -> None:
    new_project = Project(name = idea.name, description = idea.description)
    new_project.save()
    for support in IdeaSupport.objects.filter(idea=idea): # pyre-ignore[16]
        new_ownership = ProjectMembership(project = new_project, user = support.user, owner = True)
        new_ownership.save()
        support.delete()
    idea.delete()
    # TODO: message involved users to tell them this has happened
    return new_project.id # pyre-ignore[16] ("Project has no attribute id")

# ---

class ProjectView(DetailView):
    model = Project
    def post(self, request: WSGIRequest, pk: int) -> HttpResponse:
        # TODO: request to join and leave. the last owner should be unable to leave and orphan the project without shutting it down first
        return super().get(request, pk)
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        context = super().get_context_data(**kwargs)
        context['owners'] = ProjectMembership.objects.filter(project=context['object'].pk, owner = True) # pyre-ignore[16]
        context['members'] = ProjectMembership.objects.filter(project=context['object'].pk)
        return context

class AllProjectsView(TemplateView):
    def post(self, request: WSGIRequest) -> HttpResponse: # needed to receive post with to_view as mentioned in get_context_data below
        return super().get(request)
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        context = super().get_context_data(**kwargs)
        # TODO?: actual search of projects?
        if ('to_view' in self.request.POST and self.request.POST['to_view'] == 'mine'): # pyre-ignore[16]
            context['projects'] = [ownership.project for ownership in
                                   ProjectMembership.objects.filter(user=self.request.user)] # pyre-ignore[16]
            context['viewing'] = 'mine'
        else:
            context['projects'] = Project.objects.all() # pyre-ignore[16]
        return context

class EditProjectView(UpdateView):
    model = Project
    fields = ['name', 'description']
    def get(self, *args: List[Any], **kwargs: Dict[str, Any]) -> HttpResponse:
        return login_required(super().get)(*args, **kwargs) # login_required is idempotent so we may as well apply it here in case it's forgotten in urls.py
    def post(self, request: WSGIRequest, pk: int, **kwargs: Dict[str,Any]) -> HttpResponse: # pyre-ignore[14]
        project = Project.objects.get(id=pk) # pyre-ignore[16]
        if (ProjectMembership.objects.get(project=project, user=request.user).owner == True): # pyre-ignore[16]
            project.name = request.POST['name']
            project.description = request.POST['description']
            project.save()
        return redirect(reverse('view_project', args=[pk]))
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        context = super().get_context_data(**kwargs)
        context['ownerships'] = ProjectMembership.objects.filter(project=context['object'], owner = True) # pyre-ignore[16]
        return context
