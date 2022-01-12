# pyre-strict
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import CustomUser, UserRequest
from .forms import CustomUserUpdateForm, CustomUserPersonalForm

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


def profile_view(request: WSGIRequest) -> HttpResponse:
    return render(request, 'account/view.html')


class CustomUserPersonalView(TemplateView):
    model: Type[CustomUser] = CustomUser
    form_class: Type[CustomUserPersonalForm] = CustomUserPersonalForm

    def post(self, request: WSGIRequest) -> Union[HttpResponse, HttpResponseRedirect]:
        # pyre-ignore[16]:
        currentuser = request.user
        form = CustomUserPersonalForm(request.POST)
        if currentuser.year_of_birth is not None:
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


'''
class CustomUserLoginView(TemplateView):
    model: Type[CustomUser] = CustomUser

    # form_class: Type[CustomUserLoginForm] = CustomUserLoginForm

    def check_username(request: WSGIRequest) -> HttpResponse:
        usermail = request.POST.getlist('login')[0]
        #print(usermail)
        #print(get_user_model().objects.all())
        #print(get_user_model().objects.filter(email=usermail).exists())
        if (get_user_model().objects.filter(email=usermail).exists()):
            return HttpResponse("Please enter your password")
        else:
            return HttpResponse("Such an address does not exist")
'''


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
            avatar = request.FILES.get('avatar')
            currentuser.display_name = currentuser.display_name
            currentuser.email = currentuser.email
            currentuser.avatar = avatar
            currentuser.save()
            return HttpResponseRedirect(reverse_lazy('account_view'))
        else:
            display_name = form.data.get('display_name')
            currentuser.display_name = display_name
            currentuser.email = currentuser.email
            currentuser.avatar = currentuser.avatar
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
    # pyre-ignore[16]:
    stale_addresses = EmailAddress.objects.filter(
        user=email_address.user).exclude(primary=True).delete()


class CustomUserDeleteView(TemplateView):
    model: Type[CustomUser] = CustomUser
    success_url: str = reverse_lazy('account_update')

    def post(self, request: WSGIRequest) -> HttpResponse:
        if (request.POST['confirm'] == 'confirm'):
            request.user.delete()  # pyre-ignore[16]
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
            new_request = UserRequest(kind=httpreq.POST['kind'],
                                      reason=httpreq.POST['reason'],
                                      user=httpreq.user,  # pyre-ignore[16] pyre has a older version of django in mind?
                                      date=timezone.now())
            new_request.save()
        return redirect(reverse('account_update'))
    else:
        return render(httpreq, 'account/make_request.html')


@login_required(login_url='/account/login/')
def admin_request_view(httpreq: WSGIRequest) -> HttpResponse:
    ctx = {}
    # just in case the template is changed or leaks information in future:
    if httpreq.user.is_superuser:  # pyre-ignore[16]
        ctx = {'reqs': UserRequest.objects.order_by('date')}  # pyre-ignore[16]
        if (httpreq.method == 'POST'):
            if (httpreq.POST['accept'] == 'reject'):
                UserRequest.objects.get(id=httpreq.POST['request_id']).delete()
            elif (httpreq.POST['accept'] == 'accept'):
                req = UserRequest.objects.get(id=httpreq.POST['request_id'])
                usr = req.user
                if (req.kind == 'make_moderator'):
                    usr.is_staff = True
                elif (req.kind == 'change_dob'):
                    usr.year_of_birth = httpreq.POST['new_dob'][0:4]  # take the year
                elif (req.kind == 'change_postcode'):
                    usr.post_code = httpreq.POST['new_postcode']
                usr.save()
                req.delete()
    return render(httpreq, 'account/manage_requests.html', context=ctx)


# helper for inspecting db whether user exists
def check_email(request: WSGIRequest) -> HttpResponse:
    usermail = request.POST.getlist('login')[0]
    if (get_user_model().objects.filter(email=usermail).exists()):
        return HttpResponse("<span id='email-feedback' class='text-correct'>Please enter your password.</span>")
    else:
        return HttpResponse("<span id='email-feedback' class='text-incorrect'>Such an address does not exist.</span>")
