# pyre-strict
from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth.decorators import login_required

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from userauth.models import CustomUser # pyre-ignore[21]
from resources.models import Resource, FoundUseful # pyre-ignore[21]

@login_required(login_url='/profile/login/')  # redirect when user is not logged in
def dashboard(request: HttpRequest) -> HttpResponse:
    current_user = request.user
    if not current_user.added_data: # pyre-ignore[16]
        return HttpResponseRedirect(reverse('account_add_data'))

    #TODO: Load real content
    messages = ['message one', 'message two', 'message three', 'message four', 'message five']
    notifications = ['A new swimmer, Gerry, just joined Halloween Festival!', 'Good news folks we are launching a new river. Please check it out if you are interested.', 'A new resource, Writing business plans, is now available!']
    rivers = ['rivers one', 'rivers two', 'rivers three']
    #resources = ['fav resource one', 'fav resource two', 'fav resource three', 'fav resource four']
    resources = []
    useful_resources = None
    try:
        useful_resources = FoundUseful.objects.filter(found_useful_by=current_user).values()
        for resource in useful_resources:
            resource_object = Resource.objects.get(pk=resource['useful_resource_id'])
            resources.append(resource_object)

    except FoundUseful.DoesNotExist:
        print('no favourites')

    context = {
        'messages': messages,
        'notifications': notifications,
        'rivers': rivers,
        'resources': resources,
        'user': request.user,
    }
    return render(request, 'dashboard/dashboard.html', context)

