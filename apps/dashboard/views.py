# pyre-strict
from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth.decorators import login_required

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from userauth.models import CustomUser


@login_required(login_url='/account/login/')  # redirect when user is not logged in
def dashboard(request: HttpRequest) -> HttpResponse:
    print(request.user)
    if not request.user.added_data:
        return HttpResponseRedirect(reverse('account_add_data'))
    return render(request, 'dashboard/dashboard.html')
