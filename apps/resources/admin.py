from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register
)
from .models import Resource

@modeladmin_register
class ResourceAdmin(ModelAdmin):
    model = Resource
    menu_label = "Resources"
    menu_icon = "placeholder"
    menu_order = 290
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("title", "content")  # pyre-ignore[15]
    search_fields = ("title", "content")

