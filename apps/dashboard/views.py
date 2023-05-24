# pyre-strict
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse
from django.forms import Form

from django.contrib.auth.decorators import login_required

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.generic.edit import FormView

from userauth.models import CustomUser # pyre-ignore[21]
from resources.models import Resource, SavedResource # pyre-ignore[21]
from river.models import River, RiverMembership # pyre-ignore[21]
from dashboard.forms import ContactForm # pyre-ignore[21]

from typing import Tuple, Union

import requests

def get_weather(postcode: str) -> Tuple[str,str,Union[str,float]]:
    try:
        # try postcode in gb, then ie
        try:
            code_location = requests.get('https://api.openweathermap.org/geo/1.0/zip?zip=' + postcode + ',GB&appid=' + settings.WEATHER_API_KEY)
        except requests.exceptions.ConnectionError:
            code_location = requests.get('https://api.openweathermap.org/geo/1.0/zip?zip=' + postcode + ',IE&appid=' + settings.WEATHER_API_KEY)
            if code_location.status_code != 200:
                return ('[no data]', 'https://openweathermap.org/img/wn/01d@2x.png', '[no data]')

        if code_location.status_code != 200:
            return ('[no data]', 'https://openweathermap.org/img/wn/01d@2x.png', '[no data]')

        weather = requests.get('https://api.openweathermap.org/data/2.5/weather?lat=' + str(code_location.json()['lat']) + '&lon=' + str(code_location.json()['lon']) + '&appid=' + settings.WEATHER_API_KEY).json()
        desc = weather['weather'][0]['description']
        image = {'clear sky': 'https://openweathermap.org/img/wn/01d@2x.png',
            'few clouds': 'https://openweathermap.org/img/wn/02d@2x.png',
            'overcast clouds': 'https://openweathermap.org/img/wn/02d@2x.png',
            'scattered clouds': 'https://openweathermap.org/img/wn/03d@2x.png',
            'broken clouds': 'https://openweathermap.org/img/wn/04d@2x.png',
            'shower rain': 'https://openweathermap.org/img/wn/09d@2x.png',
            'light rain': 'https://openweathermap.org/img/wn/09d@2x.png',
            'rain': 'https://openweathermap.org/img/wn/10d@2x.png',
            'thunderstorm': 'https://openweathermap.org/img/wn/11d@2x.png',
            'snow': 'https://openweathermap.org/img/wn/13d@2x.png',
            'mist': 'https://openweathermap.org/img/wn/50d@2x.png',}[desc]
        temp = round(weather['main']['temp'] - 273.15, 1)
        return (desc, image, temp)
    except requests.exceptions.ConnectionError:
        return ('[no data]', 'https://openweathermap.org/img/wn/01d@2x.png', '[no data]')
    # catch all for our yet unknown error to be found in the logs
    except Exception as e:
        print('weather error')
        print(e)
        return ('[no data]', 'https://openweathermap.org/img/wn/01d@2x.png', '[no data]')

@login_required(login_url='/profile/login/')  # redirect when user is not logged in
def dashboard(request: HttpRequest) -> HttpResponse:
    current_user = request.user
    if not current_user.added_data: # pyre-ignore[16]
        return HttpResponseRedirect(reverse('account_add_data'))

    #notifications = ['A new swimmer, Gerry, just joined Halloween Festival!', 'Good news folks we are launching a new river. Please check it out if you are interested.', 'A new resource, Writing business plans, is now available!']
    rivers = []

    all_rivers = River.objects.all()

    for river in all_rivers:
        try:
            # members = RiverMembership.objects.get(user=request.user, river=river)
            members = RiverMembership.objects.filter(river=river)
            river.membership = members
            river.started_months_ago = river.get_started_months_ago
            river.current_stage = river.get_current_stage_string
            rivers.append(river)
        except RiverMembership.DoesNotExist:
            pass

    #resources = ['fav resource one', 'fav resource two', 'fav resource three', 'fav resource four']
    resources = []
    saved_resources = None
    try:
        saved_resources = SavedResource.objects.filter(saved_by=current_user).values()
        for resource in saved_resources:
            resource_object = Resource.objects.get(pk=resource['saved_resource_id'])
            resources.append(resource_object)

    except SavedResource.DoesNotExist:
        print('no favourites')

    context = {
            'rivers': rivers,
            'resources': resources,
            'user': request.user,
            }

    if current_user.post_code != None: # pyre-ignore[16]
        weather_desc, weather_img, temperature = get_weather(current_user.post_code.code) # pyre-ignore[16]
        context['temperature'] = temperature # pyre-ignore[6]
        context['weather_img'] = weather_img # pyre-ignore[6]
        context['weather_description'] = weather_desc # pyre-ignore[6]

    return render(request, 'dashboard/dashboard.html', context)


def contact(request: HttpRequest) -> HttpResponse:
    if request.method != 'POST':
        return HttpResponseNotAllowed([request.method])

    form = ContactForm(request.POST)
    if form.is_valid():
        form.send_email()
        return HttpResponse('<div class="text-large">Thank you getting in touch!</div>')
    else:
        return render(
            request,
            "dashboard/partials/get_in_touch_form.html",
            {"form": form},
        )