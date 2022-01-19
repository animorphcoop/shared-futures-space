# pyre-strict

from userauth.util import get_system_user, get_userpair
from django.core.handlers.wsgi import WSGIRequest
from project.models import ProjectMembership
from django.http import HttpResponse
from messaging.models import Message
from action.models import Action

def invoke_action_view(request: WSGIRequest) -> HttpResponse:
    if request.method == 'POST':
        action = Action.objects.get(uuid=request.POST['action_id'])
        if (action.receiver == request.user):
            if (request.POST['choice'] == 'invoke'):
                invoke_action(action)
            else:
                action.delete()
            return HttpResponse("action completed (TODO: redirect? how will this be invoked?)")
        else:
            return HttpResponse("you do not have the right to invoke this action")
    else:
        return HttpResponse("the one-time action view expects a POST request (if this doesn't make sense to you, you probably shouldn't be here")

def invoke_action(action) -> None:
    if (action.kind == 'become_owner'):
        membership = ProjectMembership.objects.get(user=action.receiver, project=action.param_project)
        if not membership.owner:
            membership.owner = True
            membership.save()
            Message.objects.create(sender=get_system_user(), chat=action.param_project.chat,
                                   snippet='<i>'+action.receiver.display_name + ' became an owner (invited by '
                                   + action.creator.display_name + ')</i>')
            Message.objects.create(sender=get_system_user(), chat=get_userpair(action.creator, action.receiver).chat,
                                   snippet='<i>'+action.receiver.display_name + ' accepted ' + action.creator.display_name
                                   + "'s offer to be an owner of " + action.param_project)
    action.delete()
