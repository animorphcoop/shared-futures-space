from typing import Dict, Optional, Tuple, Type

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form: Type[UserCreationForm] = UserCreationForm
    form: Type[UserChangeForm] = UserChangeForm
    model = CustomUser
    # need to override too-strict inferred type
    list_display: Tuple[str, ...] = (
        "pk",
        "email",
        "display_name",
        "year_of_birth",
        "post_code",
    )
    search_fields = (
        "display_name",
        "post_code",
    )
    fieldsets: Tuple[Tuple[Optional[str], Dict[str, Tuple[str, ...]]], ...] = (
        (_("Personal info"), {"fields": ("email",)}),
        (None, {"fields": ("display_name", "year_of_birth", "post_code", "avatar")}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
