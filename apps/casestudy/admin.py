from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register
)
from .models import CaseStudy



@modeladmin_register
class CasestudyAdmin(ModelAdmin):

# Register your models here.
    model = CaseStudy
    menu_label = "Case Study"
    menu_icon = "placeholder"
    menu_order = 290
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("title", "summary", "case_study_image", "body")  # pyre-ignore[15]
    search_fields = ("title", "summary")

