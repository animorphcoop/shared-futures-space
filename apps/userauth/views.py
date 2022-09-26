# pyre-strict
from allauth.utils import get_form_class
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.db.models import Q
from .models import CustomUser, UserPair, Organisation, UserAvatar
from django.contrib.auth import get_user_model
from .forms import CustomUserUpdateForm, CustomUserPersonalForm, CustomLoginForm, CustomResetPasswordForm
from django.http.request import QueryDict

from .tasks import send_after
from messaging.views import ChatView  # pyre-ignore[21]
from messaging.util import send_system_message, get_requests_chat  # pyre-ignore[21]
from action.models import Action  # pyre-ignore[21]
from area.models import PostCode  # pyre-ignore[21]

from allauth.account.adapter import DefaultAccountAdapter

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage
from typing import Type, List, Dict, Union, Any

from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed
from allauth.account.views import LoginView, SignupView, PasswordResetView

from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
from django.http import HttpResponse
from uuid import UUID
from core.utils.postcode_matcher import filter_postcode  # pyre-ignore[21]

import random


def profile_view(request: WSGIRequest) -> HttpResponse:
    return render(request, 'account/view.html')


# adding all the data required via /account/add_data/
class CustomUserPersonalView(TemplateView):
    model: Type[CustomUser] = CustomUser
    form_class: Type[CustomUserPersonalForm] = CustomUserPersonalForm

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super(CustomUserPersonalView, self).get_context_data(**kwargs)
        context['organisations'] = Organisation.objects.all()
        context['avatars'] = UserAvatar.objects.all()
        return context

    def post(self, request: WSGIRequest) -> Union[HttpResponse, HttpResponseRedirect]:
        current_user: CustomUser = request.user  # pyre-ignore[9]
        form = CustomUserPersonalForm(request.POST)  # pyre-ignore[6]
        print(form.is_valid())
        if current_user.year_of_birth is not None or current_user.post_code is not None:
            return HttpResponse(
                "You cannot change these values yourself once they are set. Instead, make a request to the administrators via the profile edit page.")
        else:
            if form.is_valid():
                print(form.cleaned_data)
                form.full_clean()
                current_user.display_name = str(form.cleaned_data.get('display_name'))
                current_user.year_of_birth = int(form.cleaned_data.get('year_of_birth'))
                current_user.post_code = \
                    PostCode.objects.get_or_create(code=filter_postcode(form.cleaned_data.get('post_code')))[0]

                if len(form.cleaned_data.get('avatar')) > 0:
                    current_user.avatar = \
                        UserAvatar.objects.get_or_create(pk=form.cleaned_data.get('avatar'))[0]
                else:
                    random_avatar = random.randint(1, UserAvatar.objects.count())
                    current_user.avatar = \
                        UserAvatar.objects.get_or_create(pk=random_avatar)[0]

                if len(form.cleaned_data.get('organisation_name')) > 0:
                    lower_org_name = form.cleaned_data.get('organisation_name').lower()
                    if Organisation.objects.filter(name__iexact=lower_org_name).exists():
                        current_user.organisation = \
                            get_object_or_404(Organisation, name=form.cleaned_data.get('organisation_name'))
                    else:
                        new_organisation = \
                            Organisation.objects.get_or_create(name=form.cleaned_data.get('organisation_name'),
                                                               link=form.cleaned_data.get('organisation_url'))[0]
                        current_user.organisation = new_organisation

                else:
                    current_user.organisation = None
                current_user.added_data = True

                current_user.save()

                return HttpResponseRedirect(reverse_lazy('dashboard'))
            else:
                print("Missing fields? Request data: ", request.POST)
                return HttpResponseRedirect(reverse('account_add_data'))


class CustomUserUpdateView(TemplateView):
    model: Type[CustomUser] = CustomUser
    form_class: Type[CustomUserUpdateForm] = CustomUserUpdateForm

    # If changing the username only - need to ensure the email does not get wiped out
    def put(self, request: WSGIRequest, *args: tuple[str, ...], **kwargs: dict[str, Any]) -> Union[
        HttpResponse, HttpResponse]:

        current_user = request.user
        print(request.body)
        data = QueryDict(request.body).dict()

        print(data)
        form = CustomUserUpdateForm(data, instance=current_user)

        print(form)
        if form.is_valid():

            current_email = current_user.email  # pyre-ignore[16]
            new_email: Union[str, list[object], None] = data.get('email')

            current_user.display_name = data.get('display_name')  # pyre-ignore[16]

            if current_email != new_email:
                print('trying to change email')
                add_email_address(request, new_email)
            else:
                print('the same email')
            current_user.email = current_email  # pyre-ignore[16]
            current_user.save()
            return profile_view(request)

        else:
            print("form is invalid")
            print(form.errors)
            return HttpResponse("Failed to retrieve or process the change, please refresh the page")


# TODO: is this actually used anywhere? can't find it if so
def post(request: WSGIRequest, *args: tuple[str, ...], **kwargs: dict[str, Any]) -> Union[HttpResponse, HttpResponse]:
    current_user = request.user
    data = QueryDict(request.body).dict()
    current_email = current_user.email  # pyre-ignore[16]
    new_email = data.get('email')
    form = CustomUserUpdateForm(data, instance=current_user)
    if form.is_valid():

        current_user.display_name = data.get('display_name')  # pyre-ignore[16]

        if current_email != new_email:
            print('trying to change email')
            add_email_address(request, new_email)
        else:
            print('the same')
        current_user.email = current_email  # pyre-ignore[16]
        current_user.save()
        return profile_view(request)

    else:
        return HttpResponse("Failed to retrieve or process the change, please refresh the page")


def add_email_address(request: WSGIRequest, new_email: Union[str, list[object], None]) -> None:
    # Add a new email address for the user, and send email confirmation.
    # Old email will remain the primary until the new one is confirmed.
    return EmailAddress.objects.add_email(request, request.user, new_email, confirm=True)


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
        return redirect(reverse('account_view'))


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
        send_system_message(get_requests_chat(), 'user_request', context_action=new_request)
        return redirect(reverse('account_update'))
    else:
        return render(httpreq, 'account/make_request.html')


class AdminRequestView(ChatView):  # pyre-ignore[11]
    def post(self, request: WSGIRequest) -> HttpResponse:
        # pyre-ignore[16]:
        return super().post(request, members=[], chat=get_requests_chat,
                            url=reverse('account_request_panel'))

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        # pyre-ignore[16]:
        if self.request.user.is_superuser:
            # pyre-ignore[16]:
            context = super().get_context_data(members=[], chat=get_requests_chat(),
                                               url=reverse('account_request_panel'))
            context['user_anonymous_message'] = ''
            context['not_member_message'] = ''
            return context
        else:
            return {}


class UserChatView(ChatView):
    def post(self, request: WSGIRequest, other_uuid: UUID) -> HttpResponse:
        [user1, user2] = sorted([request.user.uuid, other_uuid])  # pyre-ignore[16]
        userpair, _ = UserPair.objects.get_or_create(user1=CustomUser.objects.get(uuid=user1),
                                                     user2=CustomUser.objects.get(uuid=user2))
        return super().post(request, chat=userpair.chat, url=reverse('user_chat', args=[other_uuid]),  # pyre-ignore[16]
                            members=[CustomUser.objects.get(uuid=user1), CustomUser.objects.get(uuid=user2)])

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        [user1, user2] = sorted([self.request.user.uuid, kwargs['other_uuid']])  # pyre-ignore[16]
        userpair, _ = UserPair.objects.get_or_create(user1=CustomUser.objects.get(uuid=user1),
                                                     user2=CustomUser.objects.get(uuid=user2))
        # pyre-ignore[16]:
        context = super().get_context_data(chat=userpair.chat, url=reverse('user_chat', args=[kwargs['other_uuid']]),
                                           members=[CustomUser.objects.get(uuid=user1),
                                                    CustomUser.objects.get(uuid=user2)])
        context['other_user'] = CustomUser.objects.get(uuid=kwargs['other_uuid'])
        # due to the page being login_required, there should never be anonymous users seeing the page
        # due to request.user being in members, there should never be non-members seeing the page
        return context


class UserAllChatsView(TemplateView):
    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['users_with_chats'] = (
                [pair.user2 for pair in  # in the case that a chat with yourself exists, ~Q... avoids retrieving it
                 UserPair.objects.filter(~Q(user2=self.request.user), user1=self.request.user)]
                + [pair.user1 for pair in
                   UserPair.objects.filter(~Q(user1=self.request.user), user2=self.request.user)])
        return context


# helper for inspecting db whether user exists
def check_email(request: WSGIRequest) -> HttpResponse:  # should be HttpResponse?
    # print(request.META.get('HTTP_REFERER'))
    if request.POST.getlist('email'):
        user_mail = request.POST.getlist('email')[0]
        request_source_url = request.META.get('HTTP_REFERER').rsplit('/', 2)[1]
        if request_source_url == "signup":
            if get_user_model().objects.filter(email=user_mail).exists():
                return HttpResponse('This address is taken, please choose a different one.')
            else:
                return HttpResponse('')
        else:
            return HttpResponse("Could not process your request, please refresh the page or get in touch.")

    else:
        return HttpResponse("Could not process your request, please refresh the page or get in touch.")


class CustomLoginView(LoginView):
    form_class: Type[CustomLoginForm] = CustomLoginForm


class CustomPasswordResetView(PasswordResetView):
    form_class: Type[CustomResetPasswordForm] = CustomResetPasswordForm


'''
def user_detail(request: WSGIRequest, pk: int) -> Union[HttpResponse, HttpResponse]:
    user = get_object_or_404(CustomUser, pk=pk)
    context = {'user': user}
    return render(request, 'account/view_only.html', context)
'''


# make the path from name and pk
def user_detail(request: WSGIRequest, slug: str) -> Union[HttpResponse, HttpResponse]:
    split_slug = slug.rsplit('-')
    pk = split_slug[-1]
    display_name = [' '.join(split_slug[:-1])]
    if CustomUser.objects.filter(pk=pk).exists():
        user = get_object_or_404(CustomUser, pk=pk)
        if str(user.display_name).lower() == display_name[0].lower():
            context = {'user': user}
            return render(request, 'account/view_only.html', context)
        else:
            return HttpResponseRedirect(reverse('404'))
    else:
        return HttpResponseRedirect(reverse('404'))
