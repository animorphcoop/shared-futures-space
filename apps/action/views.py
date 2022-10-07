# pyre-strict

from userauth.util import get_system_user, get_userpair # pyre-ignore[21]
from django.core.handlers.wsgi import WSGIRequest
from project.models import ProjectMembership # pyre-ignore[21]
from django.http import HttpResponse
from messaging.models import Message # pyre-ignore[21]
from messaging.util import send_system_message # pyre-ignore[21]
from userauth.util import get_system_user, get_userpair
from django.utils.html import escape
from action.models import Action # pyre-ignore[21]

def invoke_action_view(request: WSGIRequest) -> HttpResponse:
    if request.method == 'POST':
        action = Action.objects.get(uuid=request.POST['action_id'], result__isnull = True) # find only actions that haven't run yet
        if (action.receiver == request.user or (action.receiver == None and request.user.is_superuser)): # pyre-ignore[16]
            if (request.POST['choice'] == 'invoke'):
                invoke_action(action)
                return HttpResponse("action completed (TODO: redirect? how will this be invoked?)")
            elif (request.POST['choice'] == 'reject'):
                reject_action(action)
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
            print('!!! WARNING B !!! not sending a message to the project, because projects no longer have one central chat. how to disseminate that information?')
            #send_system_message(action.param_project.chat, 'new_owner',
            #                    context_user_a = action.receiver, context_user_b = action.creator)
    elif (action.kind == 'become_champion'):
        membership = ProjectMembership.objects.get(user=action.receiver, project=action.param_project)
        if not membership.champion:
            membership.champion = True
            membership.save()
            print('!!! WARNING A !!! not sending a message to the project, because projects no longer have one central chat. how to disseminate that information?')
            #send_system_message(action.param_project.chat, 'new_champion',
            #                    context_user_a = action.receiver, context_user_b = action.creator)
    elif (action.kind.startswith('user_request_')):
        # TODO: actions have the option to automatically do the thing based on info given by user
        #if (action.kind == 'user_request_make_editor'):
        #    if not action.creator.editor:
        #        action.creator.editor = True
        #        action.creator.save()
        #elif (action.kind == 'user_request_change_postcode'):
        #    pass # ...
        send_system_message(get_userpair(get_system_user(), action.creator).chat, 'request_accepted', context_action = action)
    action.result = 'invoked'
    action.save()

def reject_action(action: Action) -> None:
    if (action.kind.startswith('user_request_')):
        send_system_message(get_userpair(get_system_user(), action.creator).chat, 'request_rejected', context_action = action)
    action.result = 'rejected'
    action.save()
