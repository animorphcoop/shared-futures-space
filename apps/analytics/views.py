# pyre-strict

from django.views.generic.base import TemplateView

from area.models import Area # pyre-ignore[21]
from project.models import Project, ProjectMembership # pyre-ignore[21]
from core.utils.tags_declusterer import tag_cluster_to_list # pyre-ignore[21]

from typing import Dict, Any

class AnalyticsView(TemplateView):
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        ctx = super().get_context_data(**kwargs)
        ctx['areas'] = {}
        for area in Area.objects.all():
            ctx['areas'][area.name] = {}
            ctx['areas'][area.name]['projects'] = Project.objects.filter(area = area)
            for project in ctx['areas'][area.name]['projects']:
                project.tags = tag_cluster_to_list(project.tags)
                project.swimmers = ProjectMembership.objects.filter(project = project).values_list('user', flat=True)
        print(ctx)
        return ctx
