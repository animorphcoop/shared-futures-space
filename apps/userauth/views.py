import random
from typing import Any, Dict, List, Type, Union
from urllib.parse import parse_qs, urlparse
from uuid import UUID

from action.models import Action
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed
from allauth.account.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetFromKeyView,
    PasswordResetView,
    SignupView,
)
from area.models import PostCode, get_postcode
from core.utils.postcode_matcher import filter_postcode
from django.conf import settings
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.http.request import QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from messaging.forms import ChatForm
from messaging.models import Message
from messaging.util import get_requests_chat, send_system_message
from messaging.views import ChatView
from userauth.forms import (
    CustomChangePasswordForm,
    CustomLoginForm,
    CustomResetPasswordForm,
    CustomResetPasswordKeyForm,
    CustomSignupForm,
    CustomUserAddDataForm,
    CustomUserAvatarUpdateForm,
    CustomUserNameUpdateForm,
    CustomUserOrganisationUpdateForm,
    CustomUserPostcodeUpdateForm,
)
from userauth.models import Block, CustomUser, Organisation, UserAvatar, UserPair
from userauth.tasks import send_after
from userauth.util import get_userpair, slug_to_user, user_to_slug


# redirecting to the profile url using the request data
def profile_view(
    request: WSGIRequest,
) -> Union[HttpResponseRedirect, HttpResponsePermanentRedirect]:
    if request.user.is_authenticated:
        slug = user_to_slug(request.user)
        return redirect("user_detail", slug)
    else:
        return HttpResponseRedirect(reverse_lazy("account_login"))


# adding all the data required via /profile/add_data/
class CustomAddDataView(TemplateView):
    model: Type[CustomUser] = CustomUser
    form_class: Type[CustomUserAddDataForm] = CustomUserAddDataForm

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super(CustomAddDataView, self).get_context_data(**kwargs)
        context["organisations"] = Organisation.objects.all()
        context["avatars"] = UserAvatar.objects.all()
        return context

    def post(self, request: WSGIRequest) -> Union[HttpResponse, HttpResponseRedirect]:
        current_user: CustomUser = request.user
        form = CustomUserAddDataForm(request.POST)
        if current_user.year_of_birth is not None or current_user.post_code is not None:
            return HttpResponse(
                "You cannot change these values yourself once they are set. "
                "Instead, make a request to the administrators via the profile edit page."
            )

        form = CustomUserAddDataForm(request.POST)
        if not form.is_valid():
            print("Missing fields? Request data: ", request.POST)
            return HttpResponseRedirect(reverse("account_add_data"))

        form.full_clean()
        current_user.display_name = str(form.cleaned_data.get("display_name"))
        current_user.year_of_birth = int(form.cleaned_data.get("year_of_birth"))

        current_user.post_code, _ = PostCode.objects.get_or_create(
            code=filter_postcode(form.cleaned_data.get("post_code"))
        )

        if len(form.cleaned_data.get("avatar")) > 0:
            current_user.avatar, _ = UserAvatar.objects.get_or_create(
                pk=form.cleaned_data.get("avatar")
            )
        else:
            random_avatar = random.randint(1, UserAvatar.objects.count())
            current_user.avatar, _ = UserAvatar.objects.get_or_create(pk=random_avatar)

        if len(form.cleaned_data.get("organisation_name")) > 0:
            lower_org_name = form.cleaned_data.get("organisation_name").lower()
            if Organisation.objects.filter(name__iexact=lower_org_name).exists():
                current_user.organisation = get_object_or_404(
                    Organisation,
                    name__iexact=form.cleaned_data.get("organisation_name").lower(),
                )
            else:
                new_organisation, _ = Organisation.objects.get_or_create(
                    name=form.cleaned_data.get("organisation_name"),
                    link=form.cleaned_data.get("organisation_url"),
                )
                current_user.organisation = new_organisation
        else:
            current_user.organisation = None

        current_user.added_data = True
        current_user.save()

        message = EmailMessage(
            "Welcome to Shared Futures Space!",
            render_to_string("userauth/account/emails/welcome.txt"),
            settings.DEFAULT_FROM_EMAIL,
            [current_user.email],
        )
        send_after.delay(1, message)

        return HttpResponseRedirect(reverse_lazy("dashboard"))


def add_email_address(
    request: WSGIRequest, new_email: Union[str, list[object], None]
) -> None:
    # Add a new email address for the user, and send email confirmation.
    # Old email will remain the primary until the new one is confirmed.
    return EmailAddress.objects.add_email(
        request, request.user, new_email, confirm=True
    )


# Gets triggered when clicking confirm button
@receiver(email_confirmed)
def update_user_email(
    request: WSGIRequest, email_address: EmailAddress, **kwargs: dict[str, Any]
) -> None:
    # Once the email address is confirmed, make new email_address primary.
    # This also sets user.email to the new email address.
    # email_address is an instance of allauth.account.models.EmailAddress
    email_address.set_as_primary()

    # Get rid of old email addresses
    stale_addresses = (
        EmailAddress.objects.filter(user=email_address.user)
        .exclude(primary=True)
        .delete()
    )


class CustomUserDeleteView(TemplateView):
    model: Type[CustomUser] = CustomUser

    # success_url: str = reverse_lazy('account_update')

    def post(self, request: WSGIRequest) -> HttpResponse:
        if request.POST["confirm"] == "confirm":
            request.user.delete()
            return redirect("/")
        return redirect(reverse("account_view"))


# for overriding default email send behaviour: https://stackoverflow.com/a/55965459
class CustomAllauthAdapter(DefaultAccountAdapter):
    def send_mail(
        self,
        template_prefix: str,
        email: Union[str, List[str]],
        context: Dict[str, str],
    ) -> None:
        msg: EmailMessage = self.render_mail(template_prefix, email, context)
        send_after.delay(5, msg)

    def get_login_redirect_url(self, request: WSGIRequest) -> str:
        if "HTTP_REFERER" in request.META:
            qs = parse_qs(urlparse(request.META["HTTP_REFERER"]).query)
        else:
            qs = {}
        if "next" in qs:
            return qs["next"][0]
        else:
            return reverse("dashboard")


@login_required(login_url="/profile/login/")
def user_request_view(httpreq: WSGIRequest) -> HttpResponse:
    if httpreq.method == "POST":
        new_request = Action.objects.create(
            creator=httpreq.user,
            receiver=None,
            kind="user_request_" + httpreq.POST["kind"],
            param_str=httpreq.POST["reason"],
        )
        send_system_message(
            get_requests_chat(), "user_request", context_action=new_request
        )
        return redirect(reverse("account_request"))
    else:
        return render(httpreq, "account/make_request.html")


class AdminRequestView(ChatView):
    def post(self, request: WSGIRequest) -> HttpResponse:
        return super().post(
            request,
            members=CustomUser.objects.filter(is_superuser=True),
            chat=get_requests_chat(),
            url=reverse("account_request_panel"),
        )

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        if self.request.user.is_superuser:
            context = super().get_context_data(
                members=CustomUser.objects.filter(is_superuser=True),
                chat=get_requests_chat(),
                url=reverse("account_request_panel"),
            )
            context["user_anonymous_message"] = ""
            context["not_member_message"] = ""
            return context
        else:
            return {}


class UserChatsMixin:
    """Adds user_chats and blocked_chats to context data"""

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["user_chats"] = []
        context["blocked_chats"] = []
        for user in CustomUser.objects.all():
            [user1, user2] = sorted([user, self.request.user], key=lambda u: u.uuid)

            user_chat = (
                UserPair.objects.annotate(message_count=Count("chat__message"))
                .filter(
                    user1=user1,
                    user2=user2,
                    message_count__gt=0,
                )
                .first()
            )

            if user_chat and user != self.request.user:
                user_chat.user = user
                messages_in_chat = Message.objects.filter(chat=user_chat.chat)
                user_chat.latest_message = (
                    messages_in_chat.latest("timestamp")
                    if len(messages_in_chat) != 0
                    else False
                )
                if user_chat.blocked:
                    blocked_object = Block.objects.filter(user_pair=user_chat)[0]
                    user_chat.blocked_by = blocked_object.blocked_by
                else:
                    user_chat.blocked_by = None
                if user_chat.blocked_by == self.request.user:
                    context["blocked_chats"].append(user_chat)
                else:
                    context["user_chats"].append(user_chat)
        return context


class UserChatView(UserChatsMixin, ChatView):
    form_class: Type[ChatForm] = ChatForm


class UserAllChatsView(UserChatsMixin, TemplateView):
    pass


def block_user_chat(request: WSGIRequest, uuid: UUID) -> HttpResponse:
    user_to_block = CustomUser.objects.filter(uuid=uuid)[0]
    user_chat = get_userpair(request.user, user_to_block)
    user_chat.block_user(request.user)

    return render(request, "account/partials/blocked.html")


# helper for inspecting db whether user exists
def check_email(request: WSGIRequest) -> HttpResponse:
    if request.POST.getlist("email"):
        user_mail = request.POST.getlist("email")[0]
        request_source_url = request.META.get("HTTP_REFERER").rsplit("/", 2)[1]
        if request_source_url == "signup":
            if get_user_model().objects.filter(email=user_mail).exists():
                return HttpResponse(
                    "This address is taken, please choose a different one."
                )
            else:
                return HttpResponse("")
        else:
            return HttpResponse(
                "Could not process your request, please refresh the page or get in touch."
            )

    else:
        return HttpResponse(
            "Could not process your request, please refresh the page or get in touch."
        )


class CustomSignupView(SignupView):
    form_class: Type[CustomSignupForm] = CustomSignupForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show_social_logins"] = settings.ENABLE_ALLAUTH_SOCIAL_LOGIN
        return context


class CustomLoginView(LoginView):
    form_class: Type[CustomLoginForm] = CustomLoginForm


class CustomPasswordChangeView(PasswordChangeView):
    form_class: Type[CustomChangePasswordForm] = CustomChangePasswordForm

    # success_url = reverse_lazy("account_view")
    def get_success_url(self) -> str:
        self.request.session["password_changed"] = "success"
        return reverse_lazy("account_view")


class CustomPasswordResetView(PasswordResetView):
    form_class: Type[CustomResetPasswordForm] = CustomResetPasswordForm


class CustomPasswordResetFromKeyView(PasswordResetFromKeyView):
    form_class: Type[CustomResetPasswordKeyForm] = CustomResetPasswordKeyForm


class CustomUserPersonalView(TemplateView):
    http_method_names = ["get", "post", "put"]

    # HTML does not send PUT only post so need to catch it as put since we need name to also update the url
    def dispatch(
        self, *args: List[Any], **kwargs: Dict[str, Any]
    ) -> Union[None, HttpResponse]:
        if self.request.POST:
            return self.put(*args, **kwargs)
        return super(CustomUserPersonalView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super(CustomUserPersonalView, self).get_context_data(**kwargs)
        return context

    def get(
        self, request: HttpRequest, *args: List[Any], **kwargs: Dict[str, str]
    ) -> Union[HttpResponse, HttpResponseRedirect]:
        try:
            user = slug_to_user(str(kwargs["slug"]))
        except:
            return HttpResponseRedirect(reverse("404"))

        context = {"user": user}
        context["user"].signup_date = user.signup_date.year
        if self.request.user == user:
            context["self"] = True
            context["organisations"] = Organisation.objects.all()
            context["avatars"] = UserAvatar.objects.all()
            context["changes"] = user.postcode_changes
            if self.request.session.has_key("password_changed"):
                password_changed = self.request.session["password_changed"]
                context["password_changed"] = password_changed
                del self.request.session["password_changed"]
        else:
            try:
                if user.uuid < self.request.user.uuid:
                    user_chat = UserPair.objects.filter(
                        user1=user, user2=self.request.user
                    )[0]
                else:
                    user_chat = UserPair.objects.filter(
                        user1=self.request.user, user2=user
                    )[0]
            except:
                user_chat = None
            context["user_chat"] = user_chat
        return render(request, "account/view.html", context)

    def put(
        self, request: WSGIRequest, *args: tuple[str, ...], **kwargs: dict[str, Any]
    ) -> Union[None, HttpResponse]:
        current_user = self.request.user
        data = QueryDict(request.body).dict()
        if data.get("display_name"):
            form = CustomUserNameUpdateForm(data, instance=current_user)
            if form.is_valid():
                current_user.display_name = form.cleaned_data.get("display_name")
                current_user.save()
                return HttpResponseRedirect(reverse("account_view"))
            else:
                return HttpResponse("Sorry, couldn't process your request, try again.")

        elif data.get("avatar"):
            form = CustomUserAvatarUpdateForm(data, instance=current_user)
            if form.is_valid():
                form.full_clean()
                current_user.avatar = form.cleaned_data.get("avatar")
                current_user.save()
                context = {"image_url": current_user.avatar.image_url}
                return render(request, "account/partials/avatar_image.html", context)
            else:
                return HttpResponse("Sorry, couldn't process your request, try again.")
        elif data.get("organisation_name"):
            form = CustomUserOrganisationUpdateForm(data, instance=current_user)
            if form.is_valid():
                lower_org_name = form.cleaned_data.get("organisation_name").lower()
                if Organisation.objects.filter(name__iexact=lower_org_name).exists():
                    current_user.organisation = get_object_or_404(
                        Organisation,
                        name__iexact=form.cleaned_data.get("organisation_name").lower(),
                    )
                else:
                    new_organisation = Organisation.objects.get_or_create(
                        name=form.cleaned_data.get("organisation_name"),
                        link=form.cleaned_data.get("organisation_url"),
                    )[0]

                    current_user.organisation = new_organisation

                current_user.save()
                context = {
                    "name": current_user.organisation.name,
                    "link": current_user.organisation.link,
                }
                return render(
                    request, "account/partials/organisation_name_link.html", context
                )
            else:
                return HttpResponse("Sorry, couldn't process your request, try again.")

        elif data.get("postcode"):
            form = CustomUserPostcodeUpdateForm(data, instance=current_user)
            if form.is_valid() and current_user.postcode_changes > 0:
                pc = get_postcode(form.cleaned_data.get("postcode"))
                current_user.post_code = pc
                current_user.postcode_changes -= 1
                current_user.save()
                return HttpResponseRedirect(reverse("account_view"))
            else:
                return HttpResponse("Sorry, couldn't process your request, try again.")
        else:
            return HttpResponse("Sorry, couldn't process your request, try again.")
