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
from typing import Type, List, Dict, Union

from django.dispatch import receiver

from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed

from django.core.handlers.wsgi import WSGIRequest

class CustomUserUpdateView(UpdateView):
    model: Type[CustomUser] = CustomUser
    form_class: Type[CustomUserUpdateForm] = CustomUserUpdateForm
    success_url: str = reverse_lazy('landing')

    # If changing the username only - need to ensure the email does not get wiped out
    def post(self, request: WSGIRequest, *args: tuple, **kwargs: dict) -> Union[HttpResponseRedirect, CustomUserUpdateForm]:
        userpklist = list(kwargs.values())
        currentuser = get_object_or_404(CustomUser, pk=userpklist[0])
        form = self.get_form()

        if form.is_valid():
            display_name = form.cleaned_data.get('display_name')
            if len(display_name) > 0:
                currentuser.display_name = display_name
                currentuser.email = currentuser.email
                currentuser.save()
                return HttpResponseRedirect(reverse_lazy('landing'))
            else:
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)


#@receiver(email_added)
#def add_user email()

# Gets triggered when clicking confirm button
@receiver(email_confirmed)
def update_user_email(sender: type, request: WSGIRequest, email_address: EmailAddress, **kwargs: dict) -> None:
    # Once the email address is confirmed, make new email_address primary.
    # This also sets user.email to the new email address.
    # email_address is an instance of allauth.account.models.EmailAddress
    email_address.set_as_primary()
    # Get rid of old email addresses
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
