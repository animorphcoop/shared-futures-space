# pyre-strict
from django.views.generic.base import TemplateView
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render


from typing import Dict, List, Any, Union
from core.utils.tags_declusterer import tag_cluster_to_list # pyre-ignore[21]

from area.models import Area # pyre-ignore[21]
from river.models import River, RiverMembership # pyre-ignore[21]


# TODO: THIS CLASS WILL BE REMOVED AND MADE ACCESSIBLE VIA SPRING APP
class SpringView(TemplateView):
    def get(self, request: HttpRequest, *args: List[Any], **kwargs: Dict[str, str]) -> Union[
        HttpResponse, HttpResponseRedirect]:
        # RETURN URL PATH
        slug = str(kwargs['slug'])
        if '-' in slug:
            name = slug.replace('-', ' ')
        else:
            name = slug

        if Area.objects.filter(name__iexact=name).exists():
            area = Area.objects.get(name__iexact=name)
        else:
            return HttpResponseRedirect(reverse('404'))

        rivers = River.objects.filter(area=area)
        # rivers = River.objects.all()
        # members = []
        for river in rivers:
            river.tags = tag_cluster_to_list(river.tags)

            river.us = RiverMembership.objects.filter(river=river)
            river.swimmers = RiverMembership.objects.filter(river=river).values_list('user', flat=True)

            # TEMP - comment below
            river.membership = RiverMembership.objects.filter(river=river)
            '''
            for rivermemb in RiverMembership.objects.filter(river=river):
                print(rivermemb.user)
                members.append(rivermemb.user)
            river.members = members
            '''
        num_swimmers = RiverMembership.objects.filter(
            river__in=River.objects.filter(area=area)).values_list('user', flat=True).distinct().count()

        # TODO: Add all members, starter and champions to the context 'river.swimmers' being ints; temp members
        context = {
            'area': area,
            'rivers': rivers,
            'num_swimmers': num_swimmers
        }

        # context is:
        #   'rivers' -> list of rivers with .tags and .swimmers set appropriately
        #   'num_swimmers' -> number of distinct swimmers involved in all rivers in this spring

        return render(request, 'river/all_rivers.html', context)

