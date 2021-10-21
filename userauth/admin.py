from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.utils.translation import gettext, gettext_lazy as _


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = CustomUser
    list_display = ['pk', 'email', 'display_name', 'year_of_birth', 'post_code']
    search_fields = ('display_name', 'post_code',)
    fieldsets = (

        (_('Personal info'), {'fields': ('email',)}),
        (None, {'fields': ('display_name', 'year_of_birth', 'post_code')
                }),
        )


'''    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email', 'display_name', 'year_of_birth', 'post_code')}))'''

admin.site.register(CustomUser, CustomUserAdmin)
