# pyre-strict
from django.shortcuts import get_object_or_404
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import CustomUser
from .forms import CustomUserUpdateForm

from .tasks import send_after

from allauth.account.adapter import DefaultAccountAdapter

from django.http import HttpResponseRedirect
from django.core.mail import EmailMessage
from typing import Type, List, Dict, Union, Any

from django.dispatch import receiver

from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed

from django.core.handlers.wsgi import WSGIRequest

from django.views.generic.detail import DetailView


class CustomUserProfileView(DetailView):
    model: Type[CustomUser] = CustomUser

    def get_context_data(self, **kwargs: dict[str, Any]) -> dict[str, str]:
        context = super().get_context_data(**kwargs)
        return context


class CustomUserUpdateView(UpdateView):
    model: Type[CustomUser] = CustomUser
    form_class: Type[CustomUserUpdateForm] = CustomUserUpdateForm
    success_url: str = reverse_lazy('landing')

    # If changing the username only - need to ensure the email does not get wiped out
    def post(self, request: WSGIRequest, *args: tuple[str, ...], **kwargs: dict[str, Any]) -> Union[
        HttpResponseRedirect, CustomUserUpdateForm]:

        # pyre-ignore[16]:
        self.object = self.get_object()
        userpklist = list(kwargs.values())
        currentuser = get_object_or_404(CustomUser, pk=userpklist[0])
        # form = self.get_form()
        form = CustomUserUpdateForm(request.POST, request.FILES)

        if request.FILES.get('avatar') != None:
            avatar = request.FILES.get('avatar')
            print('is avatar')
            currentuser.display_name = currentuser.display_name
            currentuser.email = currentuser.email
            currentuser.avatar = avatar
            currentuser.save()
            return HttpResponseRedirect(reverse_lazy('landing'))
        else:
            display_name = form.data.get('display_name')
            currentuser.display_name = display_name
            currentuser.email = currentuser.email
            currentuser.avatar = currentuser.avatar
            print('display_name')
            currentuser.save()
            return HttpResponseRedirect(reverse_lazy('landing'))


# @receiver(email_added)
# def add_user email()

# Gets triggered when clicking confirm button
@receiver(email_confirmed)
def update_user_email(request: WSGIRequest, email_address: EmailAddress,
                      **kwargs: dict[str, Any]) -> None:
    # Once the email address is confirmed, make new email_address primary.
    # This also sets user.email to the new email address.
    # email_address is an instance of allauth.account.models.EmailAddress
    email_address.set_as_primary()

    # Get rid of old email addresses
    # pyre-ignore[16]:
    stale_addresses = EmailAddress.objects.filter(
        user=email_address.user).exclude(primary=True).delete()


class CustomUserDeleteView(DeleteView):
    model: Type[CustomUser] = CustomUser
    success_url: str = reverse_lazy('landing')


# for overriding default email send behaviour: https://stackoverflow.com/a/55965459
class CustomAllauthAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix: str, email: Union[str, List[str]], context: Dict[str, str]) -> None:
        msg: EmailMessage = self.render_mail(template_prefix, email, context)
        send_after.delay(5, msg)
