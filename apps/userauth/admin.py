from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.utils.translation import gettext, gettext_lazy as _

from typing import Tuple

class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = CustomUser
    # need to override too-strict inferred type
    list_display: Tuple[str,...] = ('pk', 'email', 'display_name', 'year_of_birth', 'post_code') # pyre-ignore[15]
    # pyre comment suppresses an error caused by pyre's limited understanding of django
    search_fields = ('display_name', 'post_code',) # pyre-ignore[15]
    fieldsets = (

        (_('Personal info'), {'fields': ('email',)}),
        (None, {'fields': ('display_name', 'year_of_birth', 'post_code')
                }),
        )


'''    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email', 'display_name', 'year_of_birth', 'post_code')}))'''

# pyre comment suppresses an error caused by pyre's limited understanding of django
admin.site.register(CustomUser, CustomUserAdmin) # pyre-ignore[16]
