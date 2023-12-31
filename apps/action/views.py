from action.models import Action
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import redirect
from messaging.util import send_system_message
from river.models import RiverMembership
from userauth.util import get_system_user, get_userpair

# result


def invoke_action_view(request: WSGIRequest) -> HttpResponsePermanentRedirect:
    if request.method == "POST":
        action = Action.objects.get(
            uuid=request.POST["action_id"], result__isnull=True
        )  # find only actions that haven't run yet
        if action.receiver == request.user or (
            action.receiver is None and request.user.is_superuser
        ):
            if request.POST["choice"] == "invoke":
                invoke_action(action)
            elif request.POST["choice"] == "reject":
                reject_action(action)
        elif action.creator == request.user and request.POST["choice"] == "retract":
            rescind_action(action)
        else:
            pass
    return (
        redirect(request.META["HTTP_REFERER"])
        if "HTTP_REFERRER" in request.META
        else redirect("/")
    )


def rescind_action(action: Action) -> None:
    if action.kind == "become_starter":
        action.result = "rescinded"
        action.save()
        send_system_message(
            kind="ownership_determined",
            chat=get_userpair(action.creator, action.receiver).chat,
            context_action=action,
        )
        # send_system_message(get_userpair(get_system_user(), action.creator).chat, 'ownership_determined', context_action=action)


def invoke_action(action: Action) -> None:
    if action.kind == "become_starter":
        membership = RiverMembership.objects.get(
            user=action.receiver, river=action.param_river
        )
        if not membership.starter:
            membership.starter = True
            membership.save()
            # send_system_message(get_userpair(get_system_user(), action.creator).chat, 'request_accepted', context_action=action)
            send_system_message(
                kind="ownership_determined",
                chat=get_userpair(action.creator, action.receiver).chat,
                context_action=action,
            )

            print(
                "!!! WARNING B !!! not sending a message to the river, because projects no longer have one central chat. how to disseminate that information?"
            )
            # send_system_message(action.param_river.chat, 'new_owner',
            #                    context_user_a = action.receiver, context_user_b = action.creator)
    elif action.kind.startswith("user_request_"):
        # TODO: actions have the option to automatically do the thing based on info given by user
        # if (action.kind == 'user_request_make_editor'):
        #    if not action.creator.editor:
        #        action.creator.editor = True
        #        action.creator.save()
        # elif (action.kind == 'user_request_change_postcode'):
        #    pass # ...
        send_system_message(
            get_userpair(get_system_user(), action.creator).chat,
            "request_accepted",
            context_action=action,
        )
    action.result = "invoked"
    action.save()


def reject_action(action: Action) -> None:
    print(action.kind)
    if action.kind.startswith("user_request_"):
        send_system_message(
            get_userpair(get_system_user(), action.creator).chat,
            "request_rejected",
            context_action=action,
        )
    if action.kind == "become_starter":
        action.result = "rejected"
        action.save()
        send_system_message(
            kind="ownership_determined",
            chat=get_userpair(action.creator, action.receiver).chat,
            context_action=action,
        )
