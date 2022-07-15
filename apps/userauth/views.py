# pyre-strict
from allauth.utils import get_form_class
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.db.models import Q
from .models import CustomUser, UserPair
from django.contrib.auth import get_user_model
from .forms import CustomUserUpdateForm, CustomUserPersonalForm, CustomLoginForm

from .tasks import send_after
from messaging.views import ChatView # pyre-ignore[21]
from messaging.util import send_system_message, get_requests_chat # pyre-ignore[21]
from action.models import Action # pyre-ignore[21]

from allauth.account.adapter import DefaultAccountAdapter

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage
from typing import Type, List, Dict, Union, Any

from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed
from allauth.account.views import LoginView

from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
from django.http import HttpResponse
from uuid import UUID

import magic


def profile_view(request: WSGIRequest) -> HttpResponse:
    return render(request, 'account/view.html')


class CustomUserPersonalView(TemplateView):
    model: Type[CustomUser] = CustomUser
    form_class: Type[CustomUserPersonalForm] = CustomUserPersonalForm

    def post(self, request: WSGIRequest) -> Union[HttpResponse, HttpResponseRedirect]:
        # pyre-ignore[16]:
        currentuser: CustomUser = request.user
        form = CustomUserPersonalForm(request.POST)
        if currentuser.year_of_birth is not None or currentuser.post_code is not None:
            return HttpResponse(
                "You cannot change these values yourself once they are set. Instead, make a request to the administrators via the profile edit page.")
        elif form.is_valid():
            # pyre-ignore[16]:
            currentuser.year_of_birth = form.cleaned_data.get('year_of_birth')
            currentuser.post_code = form.cleaned_data.get('post_code')
            currentuser.save()
            return HttpResponseRedirect(reverse_lazy('dashboard'))
        else:
            return HttpResponseRedirect(reverse_lazy('account_data'))


class CustomUserUpdateView(TemplateView):
    model: Type[CustomUser] = CustomUser
    form_class: Type[CustomUserUpdateForm] = CustomUserUpdateForm

    # If changing the username only - need to ensure the email does not get wiped out
    def post(self, request: WSGIRequest, *args: tuple[str, ...], **kwargs: dict[str, Any]) -> Union[
        HttpResponseRedirect, CustomUserUpdateForm]:
        # pyre-ignore[16]:
        currentuser = request.user
        form = CustomUserUpdateForm(request.POST, request.FILES)

        if request.FILES.get('avatar') != None:
            new_avatar = request.FILES.get('avatar')
            declared_content_type = new_avatar.content_type
            actual_content_type = magic.from_buffer(new_avatar.file.read(2048), mime=True)
            if declared_content_type == actual_content_type and declared_content_type in ['image/png', 'image/jpeg', 'image/bmp']: # safe types that browsers will (should) never interpret as active. extend if you like, but make sure the format cannot be active (looking at you SVG)
                currentuser.avatar = request.FILES.get('avatar')
            else:
                print('error: invalid avatar (declared content type '+declared_content_type+', actual content type: '+actual_content_type+')')
        else:
            currentuser.display_name = form.data.get('display_name')
        currentuser.save()
        return HttpResponseRedirect(reverse_lazy('account_view'))


# Gets triggered when clicking confirm button
@receiver(email_confirmed)
def update_user_email(request: WSGIRequest, email_address: EmailAddress,
                      **kwargs: dict[str, Any]) -> None:
    # Once the email address is confirmed, make new email_address primary.
    # This also sets user.email to the new email address.
    # email_address is an instance of allauth.account.models.EmailAddress
    email_address.set_as_primary()

    # Get rid of old email addresses
    stale_addresses = EmailAddress.objects.filter(
        user=email_address.user).exclude(primary=True).delete()


class CustomUserDeleteView(TemplateView):
    model: Type[CustomUser] = CustomUser
    success_url: str = reverse_lazy('account_update')

    def post(self, request: WSGIRequest) -> HttpResponse:
        if (request.POST['confirm'] == 'confirm'):
            request.user.delete()
            return redirect('/')
        return redirect(reverse('account_update'))


# for overriding default email send behaviour: https://stackoverflow.com/a/55965459
class CustomAllauthAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix: str, email: Union[str, List[str]], context: Dict[str, str]) -> None:
        msg: EmailMessage = self.render_mail(template_prefix, email, context)
        send_after.delay(5, msg)

@login_required(login_url='/account/login/')
def user_request_view(httpreq: WSGIRequest) -> HttpResponse:
    if (httpreq.method == 'POST'):
        new_request = Action.objects.create(creator=httpreq.user, receiver=None,
                                            kind='user_request_' + httpreq.POST['kind'],
                                            param_str=httpreq.POST['reason'])
        send_system_message(get_requests_chat(), 'user_request', context_action = new_request)
        return redirect(reverse('account_update'))
    else:
        return render(httpreq, 'account/make_request.html')

class AdminRequestView(ChatView): # pyre-ignore[11]
    def post(self, request: WSGIRequest) -> HttpResponse:
        return super().post(request, members=[], chat=get_requests_chat, url=reverse('account_request_panel')) # pyre-ignore[16]
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        if self.request.user.is_superuser: # pyre-ignore[16]
            context = super().get_context_data(members=[], chat=get_requests_chat(), url=reverse('account_request_panel')) # pyre-ignore[16]
            context['user_anonynous_message'] = ''
            context['not_member_message'] = ''
            return context
        else:
            return {}

class UserChatView(ChatView):
    def post(self, request: WSGIRequest, other_uuid: UUID) -> HttpResponse:
        [user1, user2] = sorted([request.user.uuid, other_uuid]) # pyre-ignore[16]
        userpair, _ = UserPair.objects.get_or_create(user1=CustomUser.objects.get(uuid=user1),
                                                  user2=CustomUser.objects.get(uuid=user2))
        return super().post(request, chat = userpair.chat, url = reverse('user_chat', args=[other_uuid]), # pyre-ignore[16]
                            members = [CustomUser.objects.get(uuid=user1), CustomUser.objects.get(uuid=user2)])
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        [user1, user2] = sorted([self.request.user.uuid, kwargs['other_uuid']]) # pyre-ignore[16]
        userpair, _ = UserPair.objects.get_or_create(user1=CustomUser.objects.get(uuid=user1),
                                                  user2=CustomUser.objects.get(uuid=user2))
        context = super().get_context_data(chat = userpair.chat, url = reverse('user_chat', args=[kwargs['other_uuid']]), # pyre-ignore
                                           members = [CustomUser.objects.get(uuid=user1), CustomUser.objects.get(uuid=user2)])
        context['other_user'] = CustomUser.objects.get(uuid=kwargs['other_uuid'])
        # due to the page being login_required, there should never be anonymous users seeing the page
        # due to request.user being in members, there should never be non-members seeing the page
        return context

class UserAllChatsView(TemplateView):
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        context = super().get_context_data(**kwargs)
        context['users_with_chats'] = ([pair.user2 for pair in # in the case that a chat with yourself exists, ~Q... avoids retrieving it 
                                        UserPair.objects.filter(~Q(user2=self.request.user), user1 = self.request.user)]
                                     + [pair.user1 for pair in
                                        UserPair.objects.filter(~Q(user1=self.request.user), user2 = self.request.user)])
        return context

# helper for inspecting db whether user exists
# TODO: Add more validation e.g. to lower case
def check_email(request: WSGIRequest) -> HttpResponse:
    if request.POST.getlist('login'):
        user_mail = request.POST.getlist('login')[0]
        if (get_user_model().objects.filter(email=user_mail).exists()):
            return HttpResponse("<span id='email-feedback' class='text-correct'>Please enter your password.</span>")
        else:
            return HttpResponse(
                "<span id='email-feedback' class='text-incorrect'>Such an address does not exist.</span>")
    elif request.POST.getlist('email'):
        user_mail = request.POST.getlist('email')[0]
        # TODO: Better email validation might be needed!
        if ("@" not in user_mail or "." not in user_mail) or ("@" == user_mail[-1] or "." == user_mail[-1]):
            return HttpResponse(
                "<span id='email-feedback' class='text-incorrect'>Please make sure you enter an email address.</span>")
        else:
            if (get_user_model().objects.filter(email=user_mail).exists()):
                return HttpResponse(
                    "<span id='email-feedback' class='text-incorrect'>This address is in use, please choose a different one.</span>")
            else:
                return HttpResponse(
                    "<span id='email-feedback' class='text-correct'>This e-mail address is available.</span>")
    else:
        return HttpResponse("Failed to retrieve or process the address, please refresh the page")


# TODO: Add more validation e.g. to lower case
def check_display_name(request: WSGIRequest) -> HttpResponse:
    if request.POST.getlist('display_name'):
        display_name = request.POST.getlist('display_name')[0]
        if len(display_name) < 2:
            return HttpResponse(
                "<span id='name-feedback' class='text-incorrect'>Please enter a name at least 2 characters long.</span>")
        elif get_user_model().objects.filter(display_name=display_name).exists():
            return HttpResponse(
                "<span id='name-feedback' class='text-incorrect'>This name is in use, please choose a different one.</span>")
        else:
            return HttpResponse(
                "<span id='name-feedback' class='text-correct'>The name is available.</span>")

    else:
        return HttpResponse("Failed to retrieve or process the name, please refresh the page")


class CustomLoginView(LoginView):
    form_class: Type[CustomLoginForm] = CustomLoginForm
