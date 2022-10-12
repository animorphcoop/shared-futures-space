# pyre-strict

from django.views.generic.base import TemplateView

from userauth.models import CustomUser # pyre-ignore[21]
from area.models import Area # pyre-ignore[21]
from project.models import Project, ProjectMembership # pyre-ignore[21]
from core.utils.tags_declusterer import tag_cluster_to_list # pyre-ignore[21]

from typing import Dict, Any

class Graph():
    def __init__(self, title, data):
        self.title = title
        self.data = data
    def visualise(self):
        pass

class BarGraph(Graph):
    def __init__(self, title, data, scale):
        super().__init__(title, data)
        self.scale = scale
    def visualise(self):
        height = 200
        width = 60+(len(self.data)*80)
        svg = f'<svg height={height} width={width} style="stroke:black;stroke-width:1"><line x1=30 y1=30 x2=30 y2={height-10}></line><line x1=10 y1={height-30} x2={width-30} y2={height-30}></line>'
        for n in range(0,self.scale):
            svg += f'<text x=10 y={(height-30)-((height-30)*(n/self.scale))} style="font-size:8px">{n}</text>'
        for n in range(len(self.data)):
            name, bar = self.data[n]
            svg += f'<text x={30+((width-30)*n/len(self.data))} y={height-20} style="font-size:8px">{name}</text>'
            svg += f'<rect x={30+((width-30)*n/len(self.data))} y={(height-30)-((height-30)*bar/self.scale)} width=10 height={((height-30)*bar/self.scale)}></rect>'
        svg += f'</svg>'
        return svg
    def total(self):
        return sum(map(lambda t: t[1], self.data))
    def average(self):
        return self.total() / len(self.data)

class AnalyticsView(TemplateView):
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        ctx = super().get_context_data(**kwargs)
        ctx['graphs'] = []
        users_area = [(area.name, len(CustomUser.objects.filter(post_code__area = area))) for area in Area.objects.all()]
        users_scale = max(map(lambda t: t[1], users_area))
        ctx['graphs'].append(BarGraph('users/area', users_area, users_scale))
        projects_area = [(area.name, len(Project.objects.filter(area=area))) for area in Area.objects.all()]
        project_scale = max(map(lambda t: t[1], projects_area))
        ctx['graphs'].append(BarGraph('projects/area', projects_area, project_scale))
        ctx['graphs'].append(BarGraph('projects/stages - overall', [('not begun', len(Project.objects.filter(current_stage = None))),
                                                                    ('envision', len(Project.objects.filter(current_stage = Project.Stage.ENVISION))),
                                                                    ('plan', len(Project.objects.filter(current_stage = Project.Stage.PLAN))),
                                                                    ('act', len(Project.objects.filter(current_stage = Project.Stage.ACT))),
                                                                    ('reflect', len(Project.objects.filter(current_stage = Project.Stage.REFLECT)))], project_scale))
        for area in Area.objects.all():
            ctx['graphs'].append(BarGraph('projects/stages - ' + area.name, [('not begun', len(Project.objects.filter(area = area, current_stage = None))),
                                                                             ('envision', len(Project.objects.filter(area = area, current_stage = Project.Stage.ENVISION))),
                                                                             ('plan', len(Project.objects.filter(area = area, current_stage = Project.Stage.PLAN))),
                                                                             ('act', len(Project.objects.filter(area = area, current_stage = Project.Stage.ACT))),
                                                                             ('reflect', len(Project.objects.filter(area = area, current_stage = Project.Stage.REFLECT)))], project_scale))
        swimmers_area = [(area.name, (len(ProjectMembership.objects.filter(project__in = Project.objects.filter(area=area))) / len(Project.objects.filter(area=area)))
                           if len(Project.objects.filter(area=area)) != 0 else 0)
                          for area in Area.objects.all()]
        swimmers_scale = int(max(map(lambda t: t[1], swimmers_area)))+1
        ctx['graphs'].append(BarGraph('average swimmers/project', swimmers_area, swimmers_scale))
        return ctx
