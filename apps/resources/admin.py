from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import CaseStudy, HowTo


@modeladmin_register
class HowToAdmin(ModelAdmin):
    model = HowTo
    menu_label = "How Tos"
    menu_icon = "placeholder"
    menu_order = 290
    add_to_settings_menu = False
    exclude_from_explorer = False
    search_fields = ("title", "summary")


@modeladmin_register
class CaseStudyAdmin(ModelAdmin):
    model = CaseStudy
    menu_label = "Case Studies"
    menu_icon = "placeholder"
    menu_order = 290
    add_to_settings_menu = False
    exclude_from_explorer = False
    search_fields = ("title", "summary")
