# pyre-strict
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required

from .models import CustomUser, UserRequest
from .forms import CustomUserUpdateForm

from .tasks import send_after

from allauth.account.adapter import DefaultAccountAdapter

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage
from typing import Type, List, Dict, Union, Any

from django.dispatch import receiver

from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed

from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
from django.http import HttpResponse

class CustomUserUpdateView(TemplateView):
    model: Type[CustomUser] = CustomUser
    form_class: Type[CustomUserUpdateForm] = CustomUserUpdateForm

    # If changing the username only - need to ensure the email does not get wiped out

    def post(self, request: WSGIRequest) -> Union[HttpResponseRedirect, CustomUserUpdateForm]:
        currentuser = request.user # pyre-ignore[16]
        form = CustomUserUpdateForm(request.POST)

        if form.is_valid():
            display_name = form.cleaned_data.get('display_name') # pyre-ignore[16]
            if len(display_name) > 0:
                currentuser.display_name = display_name
                currentuser.email = currentuser.email
                currentuser.save()
                return HttpResponseRedirect(reverse_lazy('account_update'))
            else:
                return self.form_invalid(form) # pyre-ignore[16]
        else:
            return self.form_invalid(form)

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


class CustomUserDeleteView(TemplateView):
    model: Type[CustomUser] = CustomUser
    success_url: str = reverse_lazy('account_update')
    def post(self, request: WSGIRequest) -> HttpResponse:
        if (request.POST['confirm'] == 'confirm'):
            request.user.delete() # pyre-ignore[16]
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
        if (httpreq.POST['kind'] not in ['make_moderator', 'change_dob', 'change_postcode', 'other']):
            print('error: not a valid kind of request')
        elif (len(httpreq.POST['reason']) > 1000):
            print('error: reason too long (> 1000 chars)')
        else:
            new_request = UserRequest(kind = httpreq.POST['kind'],
                                      reason = httpreq.POST['reason'],
                                      user = httpreq.user, # pyre-ignore[16] pyre has a older version of django in mind?
                                      date = timezone.now())
            new_request.save()
        return redirect(reverse('account_update', args=[httpreq.user.id]))
    else:
        return render(httpreq, 'account/make_request.html')

@login_required(login_url='/account/login/')
def admin_request_view(httpreq: WSGIRequest) -> HttpResponse:
    if (httpreq.method == 'POST'):
        if (httpreq.POST['accept'] == 'reject'):
            UserRequest.objects.get(id=httpreq.POST['request_id']).delete() # pyre-ignore[16]
        elif (httpreq.POST['accept'] == 'accept'):
            req = UserRequest.objects.get(id=httpreq.POST['request_id'])
            usr = req.user
            if (req.kind == 'make_moderator'):
                usr.is_staff = True
            elif (req.kind == 'change_dob'):
                usr.year_of_birth = httpreq.POST['new_dob'][0:4] # take the year
            elif (req.kind == 'change_postcode'):
                usr.post_code = httpreq.POST['new_postcode']
            usr.save()
            req.delete()
    ctx = {}
    # just in case the template is changed or leaks information in future:
    if httpreq.user.is_superuser: # pyre-ignore[16]
        ctx = {'reqs': UserRequest.objects.order_by('date') }
    return render(httpreq, 'account/manage_requests.html', context=ctx)
