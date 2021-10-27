# pyre-strict
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.http import HttpRequest, HttpResponse

@login_required(login_url='/account/login/')  # redirect when user is not logged in
def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, 'dashboard/dashboard.html')
