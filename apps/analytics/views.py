# pyre-strict

from django.views.generic.base import TemplateView

from userauth.models import CustomUser # pyre-ignore[21]
from area.models import Area # pyre-ignore[21]
from river.models import River, RiverMembership # pyre-ignore[21]
from core.utils.tags_declusterer import tag_cluster_to_list # pyre-ignore[21]

from typing import Dict, List, Tuple, Any

class Graph():
    def __init__(self, title: str, data: List[Tuple[str,int]]) -> None:
        self.title = title
        self.data = data
    def visualise(self) -> str:
        return "[default graph object doesn't contain a working visualisation method]"

class BarGraph(Graph):
    def __init__(self, title: str, data: List[Tuple[str,int]], scale: int) -> None:
        super().__init__(title, data)
        self.scale = scale
    def visualise(self) -> str:
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
    def total(self) -> int:
        return sum(map(lambda t: t[1], self.data))
    def average(self) -> float:
        return self.total() / len(self.data)

class AnalyticsView(TemplateView):
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        ctx = super().get_context_data(**kwargs)
        ctx['graphs'] = []
        users_area = [(area.name, len(CustomUser.objects.filter(post_code__area = area))) for area in Area.objects.all()]
        users_scale = max(map(lambda t: t[1], users_area))
        ctx['graphs'].append(BarGraph('users/area', users_area, users_scale))
        river_area = [(area.name, len(River.objects.filter(area=area))) for area in Area.objects.all()]
        river_scale = max(map(lambda t: t[1], river_area))
        ctx['graphs'].append(BarGraph('river/area', river_area, river_scale))
        ctx['graphs'].append(BarGraph('river/stages - overall', [('not begun', len(River.objects.filter(current_stage = None))),
                                                                    ('envision', len(River.objects.filter(current_stage = River.Stage.ENVISION))),
                                                                    ('plan', len(River.objects.filter(current_stage = River.Stage.PLAN))),
                                                                    ('act', len(River.objects.filter(current_stage = River.Stage.ACT))),
                                                                    ('reflect', len(River.objects.filter(current_stage = River.Stage.REFLECT)))], river_scale))
        for area in Area.objects.all():
            ctx['graphs'].append(BarGraph('river/stages - ' + area.name, [('not begun', len(River.objects.filter(area = area, current_stage = None))),
                                                                             ('envision', len(River.objects.filter(area = area, current_stage = River.Stage.ENVISION))),
                                                                             ('plan', len(River.objects.filter(area = area, current_stage = River.Stage.PLAN))),
                                                                             ('act', len(River.objects.filter(area = area, current_stage = River.Stage.ACT))),
                                                                             ('reflect', len(River.objects.filter(area = area, current_stage = River.Stage.REFLECT)))], river_scale))
        swimmers_area = [(area.name, (len(RiverMembership.objects.filter(river__in = River.objects.filter(area=area))) / len(River.objects.filter(area=area)))
                           if len(River.objects.filter(area=area)) != 0 else 0)
                          for area in Area.objects.all()]
        swimmers_scale = int(max(map(lambda t: t[1], swimmers_area)))+1
        ctx['graphs'].append(BarGraph('average swimmers/river', swimmers_area, swimmers_scale))
        if self.request.user.is_superuser: # pyre-ignore[16]
            return ctx
        else:
            return {'unauthenticated': True}
