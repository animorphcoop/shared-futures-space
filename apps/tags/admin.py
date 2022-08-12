from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register
)
from .models import Tag

@modeladmin_register
class TagAdmin(ModelAdmin):
    model = Tag
    menu_label = "Tags"
    menu_icon = "placeholder"
    menu_order = 290
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("name",)  # pyre-ignore[15]
    search_fields = ("name",)

