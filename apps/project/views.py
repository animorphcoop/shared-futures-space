# pyre-strict

from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from .models import Project, ProjectMessage, ProjectOwnership, ProjectSupport
from typing import Dict, List, Any

class ProjectView(DetailView):
    model = Project
    def post(self, request: WSGIRequest, pk: int) -> HttpResponse:
        if (request.POST['form'] == 'give_support'):
            # you can't support your own project or support a project more than once
            if (0 == len(ProjectSupport.objects.filter(project=Project.objects.get(id=pk), # pyre-ignore[16]
                                                       user=request.user)) and # pyre-ignore[16]
                0 == len(ProjectOwnership.objects.filter(project=Project.objects.get(id=pk), # pyre-ignore[16]
                                                         user=request.user))):
                support = ProjectSupport(project=Project.objects.get(id=pk),
                                         user=request.user)
                support.save()
        elif (request.POST['form'] == 'remove_support'):
            supports = ProjectSupport.objects.filter(project=Project.objects.get(id=pk),
                                                     user=request.user)
            for support in supports:
                support.delete()
        elif (request.POST['form'] == 'message'):
            msg = ProjectMessage(project=Project.objects.get(id=pk),
                                 message=request.POST['msg'],
                                 user_from=request.user)
            msg.save()
        return super().get(request, pk)
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        context = super().get_context_data(**kwargs)
        context['owners'] = ProjectOwnership.objects.filter(project=context['object'].pk) # pyre-ignore[16]
        context['supporters'] = ProjectSupport.objects.filter(project=context['object'].pk) # pyre-ignore[16]
        if (self.request.user in [ownership.user for ownership in context['owners']]): # pyre-ignore[16]
            context['messages'] = ProjectMessage.objects.filter(project=context['object'].pk) # pyre-ignore[16]
        return context

class AllProjectsView(TemplateView):
    def post(self, request: WSGIRequest) -> HttpResponse:
        return super().get(request)
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        context = super().get_context_data(**kwargs)
        if ('to_view' in self.request.POST and self.request.POST['to_view'] == 'mine'): # pyre-ignore[16]
            context['projects'] = [ownership.project for ownership in
                                   ProjectOwnership.objects.filter(user=self.request.user)] # pyre-ignore[16]
            context['viewing'] = 'mine'
        else:
            context['projects'] = Project.objects.all() # pyre-ignore[16]
        return context

class MakeProjectView(TemplateView):
    def post(self, request: WSGIRequest, **kwargs: Dict[str,Any]) -> HttpResponse:
        new_project = Project(name=request.POST['name'], description=request.POST['description'])
        new_project.save()
        ownership = ProjectOwnership(project=new_project, user=request.user) # pyre-ignore[16]
        ownership.save()
        return redirect(reverse('all_projects'))

class EditProjectView(UpdateView):
    model = Project
    fields = ['name', 'description']
    def get(self, *args: List[Any], **kwargs: Dict[str, Any]) -> HttpResponse:
        return login_required(super().get)(*args, **kwargs)
    def post(self, request: WSGIRequest, pk: int, **kwargs: Dict[str,Any]) -> HttpResponse: # pyre-ignore[14]
        project = Project.objects.get(id=pk) # pyre-ignore[16]
        if (0 != len(ProjectOwnership.objects.filter(project=project, user=request.user))): # pyre-ignore[16]
            if ('abdicate' in request.POST and request.POST['abdicate'] == 'abdicate'
                and 1 < len(ProjectOwnership.objects.filter(project=project))):
                ownership = ProjectOwnership.objects.get(project=project, user=request.user)
                ownership.delete()
            else:
                project.name = request.POST['name']
                project.description = request.POST['description']
                project.save()
        return redirect(reverse('view_project', args=[pk]))
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        context = super().get_context_data(**kwargs)
        context['ownerships'] = ProjectOwnership.objects.filter(project=context['object']) # pyre-ignore[16]
        return context

class DeleteMessageView(View):
    def post(self, request: WSGIRequest) -> HttpResponse:
        msg = ProjectMessage.objects.get(pk=request.POST['target']) # pyre-ignore[16]
        if (request.user in [ownership.user for ownership in # pyre-ignore[16]
                             ProjectOwnership.objects.filter(project=msg.project)]): # pyre-ignore[16]
            msg.delete()
        return redirect(reverse('view_project', args=[msg.project.id]))
