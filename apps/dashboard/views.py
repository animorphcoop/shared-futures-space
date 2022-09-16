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

    messages = ['message one', 'message two', 'message three', 'message four', 'message five']
    notifications = ['A new swimmer, Gerry, just joined Halloween Festival!', 'Good news folks we are launching a new project. Please check it out if you are interested.', 'A new resource, Writing business plans, is now available!']
    rivers = ['rivers one', 'rivers two', 'rivers three']
    resources = ['fav resource one', 'fav resource two', 'fav resource three', 'fav resource four']

    context = {
        'messages': messages,
        'notifications': notifications,
        'rivers': rivers,
        'resources': resources,
    }
    return render(request, 'dashboard/dashboard.html', context)
