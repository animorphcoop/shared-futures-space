# pyre-strict

from userauth.util import get_system_user, get_userpair # pyre-ignore[21]
from django.core.handlers.wsgi import WSGIRequest
from project.models import ProjectMembership # pyre-ignore[21]
from django.http import HttpResponse
from messaging.models import Message # pyre-ignore[21]
from messaging.util import send_system_message # pyre-ignore[21]
from django.utils.html import escape
from action.models import Action # pyre-ignore[21]

def invoke_action_view(request: WSGIRequest) -> HttpResponse:
    if request.method == 'POST':
        action = Action.objects.get(uuid=request.POST['action_id'], result__isnull = True) # find only actions that haven't run yet
        if (action.receiver == request.user): # pyre-ignore[16]
            if (request.POST['choice'] == 'invoke'):
                invoke_action(action)
                return HttpResponse("action completed (TODO: redirect? how will this be invoked?)")
            elif (request.POST['choice'] == 'reject'):
                action.result = 'rejected'
                action.save()
                return HttpResponse("action rejected (TODO: redirect? how will this be invoked?)")
        elif (action.creator == request.user and request.POST['choice'] == 'retract'):
            action.result = 'rescinded'
            action.save()
            return HttpResponse("action rescinded")
        else:
            return HttpResponse("you do not have the right to invoke this action")
    return HttpResponse("the one-time action view expects a POST request (if this doesn't make sense to you, you probably shouldn't be here")

def invoke_action(action: Action) -> None: # pyre-ignore[11]
    if (action.kind == 'become_owner'):
        membership = ProjectMembership.objects.get(user=action.receiver, project=action.param_project)
        if not membership.owner:
            membership.owner = True
            membership.save()
            send_system_message(action.param_project.chat, 'new_owner',
                                context_user_a = action.creator, context_user_b = action.receiver)
    action.result = 'invoked'
    action.save()
