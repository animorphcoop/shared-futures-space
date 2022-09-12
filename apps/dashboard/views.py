# pyre-strict
from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth.decorators import login_required

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from userauth.models import CustomUser # pyre-ignore[21]


@login_required(login_url='/account/login/')  # redirect when user is not logged in
def dashboard(request: HttpRequest) -> HttpResponse:
    if not request.user.added_data: # pyre-ignore[16]
        return HttpResponseRedirect(reverse('account_add_data'))
    return render(request, 'dashboard/dashboard.html')
