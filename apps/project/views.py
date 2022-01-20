# pyre-strict

from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.decorators import login_required
from django.db.models.fields import CharField
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

from .models import Idea, IdeaSupport, Project, ProjectMembership
from messaging.models import Chat, Message # pyre-ignore[21]
from userauth.util import get_system_user, get_userpair # pyre-ignore[21]
from messaging.views import ChatView # pyre-ignore[21]
from action.util import send_offer
from action.models import Action
from typing import Dict, List, Any

class IdeaView(DetailView):
    model = Idea
    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        this_idea = Idea.objects.get(slug=slug) # pyre-ignore[16]
        if (request.POST['action'] == 'give_support'):
            # can't support one idea more than once
            if (0 == len(IdeaSupport.objects.filter(idea=this_idea, # pyre-ignore[16]
                                                    user=request.user))): # pyre-ignore[16]
                support = IdeaSupport(idea=this_idea,
                                      user=request.user)
                support.save()
                # TODO: is this the only place support can be given? if not, need to check elsewhere as well
                if (len(IdeaSupport.objects.filter(idea=Idea.objects.get(slug=slug))) >= settings.PROJECT_REQUIRED_SUPPORTERS):
                    new_project_slug = replace_idea_with_project(Idea.objects.get(slug=slug))
                    return redirect(reverse('view_project', args=[new_project_slug]))
        elif (request.POST['action'] == 'remove_support'):
            # can't remove support from your own idea (because you wouldn't be able to return it through the intended interface)
            if (request.user != this_idea.proposed_by):
                supports = IdeaSupport.objects.filter(idea=this_idea,
                                                      user=request.user)
                for support in supports: # there should only be one, but no need to assume that
                    support.delete()
        return super().get(request, slug)
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
        new_idea = Idea(name=request.POST['name'], description=request.POST['description'], proposed_by=request.user, slug="") # pyre-ignore[16]
        new_idea.save()
        new_support = IdeaSupport(idea=new_idea, user=request.user)
        new_support.save()
        return redirect(reverse('all_ideas'))

class EditIdeaView(UpdateView):
    model = Idea
    fields = ['name', 'description']
    def get(self, *args: List[Any], **kwargs: Dict[str, Any]) -> HttpResponse:
        return login_required(super().get)(*args, **kwargs) # login_required is idempotent so we may as well apply it here in case it's forgotten in urls.py
    def post(self, request: WSGIRequest, slug: str, **kwargs: Dict[str,Any]) -> HttpResponse: # pyre-ignore[14]
        idea = Idea.objects.get(slug=slug) # pyre-ignore[16]
        if request.POST['action'] == 'update':
            idea.name = request.POST['name']
            idea.description = request.POST['description']
            idea.save()
        elif request.POST['action'] == 'delete':
            idea.delete()
            return redirect(reverse('all_ideas'))
        return redirect(reverse('view_idea', args=[slug]))

# ---

def replace_idea_with_project(idea: Idea) -> CharField:
    new_chat = Chat()
    new_chat.save()
    new_project = Project(name = idea.name, description = idea.description, slug = idea.slug, chat = new_chat)
    new_project.save()
    for support in IdeaSupport.objects.filter(idea=idea): # pyre-ignore[16]
        new_ownership = ProjectMembership(project = new_project, user = support.user, owner = True)
        new_ownership.save()
        support.delete()
    idea.delete()
    # TODO: message involved users to tell them this has happened
    return new_project.slug

# ---

class ProjectView(DetailView):
    model = Project
    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        # TODO: request to join and leave.
        if (request.POST['action'] == 'leave'):
            membership = ProjectMembership.objects.get(user=request.user, project=Project.objects.get(slug=slug)) # pyre-ignore[16]
            if not membership.owner: # reject owners attempting to leave, this is not supported by the interface - you should rescind ownership first, because you won't be allowed to if you're the last owner left. TODO: allow owners to leave as well if they're not the last owner
                membership.delete()
        return super().get(request, slug)
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        context = super().get_context_data(**kwargs)
        context['owners'] = ProjectMembership.objects.filter(project=context['object'].pk, owner = True) # pyre-ignore[16]
        context['champions'] = ProjectMembership.objects.filter(project=context['object'].pk, champion = True)
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
    def post(self, request: WSGIRequest, slug: str, **kwargs: Dict[str,Any]) -> HttpResponse: # pyre-ignore[14]
        project = Project.objects.get(slug=slug) # pyre-ignore[16]
        if (ProjectMembership.objects.get(project=project, user=request.user).owner == True): # pyre-ignore[16]
            if ('abdicate' in request.POST and request.POST['abdicate'] == 'abdicate'):
                ownerships = ProjectMembership.objects.filter(project=project, owner=True)
                if (len(ownerships) >= 2): # won't be orphaning the project (TODO: allow projects to be shut down, in which case they can be orphaned)
                    my_membership = ProjectMembership.objects.get(project=project, user=request.user, owner=True)
                    my_membership.owner = False
                    my_membership.save()
            project.name = request.POST['name']
            project.description = request.POST['description']
            project.save()
        return redirect(reverse('view_project', args=[slug]))
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        context = super().get_context_data(**kwargs)
        context['ownerships'] = ProjectMembership.objects.filter(project=context['object'], owner = True) # pyre-ignore[16]
        return context

class ManageProjectView(DetailView):
    model = Project
    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        project = Project.objects.get(slug=slug) # pyre-ignore[16]
        membership = ProjectMembership.objects.get(id=request.POST['membership']) # pyre-ignore[16]
        # security checks
        if (ProjectMembership.objects.get(user=request.user, project=project).owner == True # pyre-ignore[16]
            and membership.project == Project.objects.get(slug=slug)): # since the form takes any uid
            if (request.POST['action'] == 'offer_ownership'):
                if not membership.owner: # not an owner already
                    send_offer(request.user, membership.user, 'become_owner', param_project = project)
            elif (request.POST['action'] == 'offer_championship'):
                2 # TODO: ditto
            elif (request.POST['action'] == 'remove_championship'):
                membership.champion = False
            membership.save()
        return self.get(request, slug)
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        context = super().get_context_data(**kwargs)
        context['ownerships'] = ProjectMembership.objects.filter(project=context['object'].pk, owner = True) # pyre-ignore[16]
        context['memberships'] = ProjectMembership.objects.filter(project=context['object'].pk)
        return context

class ProjectChatView(ChatView): # pyre-ignore[11] - thinks ChatView isn't a type
    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        project = Project.objects.get(slug=slug) # pyre-ignore[16]
        return super().post(request, chat = project.chat, url = reverse('project_chat', args=[slug]), # pyre-ignore[16]
                            members = [membership.user for membership
                                       in ProjectMembership.objects.filter(project=project)]) # pyre-ignore[16]
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        project = Project.objects.get(slug=kwargs['slug']) # pyre-ignore[16]
        context = super().get_context_data(slug=kwargs['slug'], chat = project.chat, url = reverse('project_chat', args=[kwargs['slug']]), # pyre-ignore[16]
                                           members = [membership.user for membership
                                                      in ProjectMembership.objects.filter(project=project)]) # pyre-ignore[16]
        context['project'] = project
        context['user_anonymous_message'] = '(you must sign in to contribute)'
        context['not_member_message'] = '(you must be a member of this project to contribute)'
        return context








