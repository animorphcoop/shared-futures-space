# pyre-strict
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.utils.translation import gettext, gettext_lazy as _

from typing import Tuple, Dict, Optional

class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = CustomUser
    # need to override too-strict inferred type
    list_display: Tuple[str,...] = ('pk', 'email', 'display_name', 'year_of_birth', 'post_code')
    # pyre comment suppresses an error caused by pyre's limited understanding of django
    search_fields = ('display_name', 'post_code',)
    fieldsets: Tuple[Tuple[Optional[str],Dict[str,Tuple[str, ...]]], ...] = (
        (_('Personal info'), {'fields': ('email',)}),
        (None, {'fields': ('display_name', 'year_of_birth', 'post_code', 'avatar')}),
        )

# pyre comment suppresses an error caused by pyre's limited understanding of django
admin.site.register(CustomUser, CustomUserAdmin)
