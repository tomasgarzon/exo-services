from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from . import models
from .forms import UserAddForm


@admin.register(models.User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('_username', 'password')}),
        (_('Personal info'), {'fields': ('short_name', 'full_name', 'email', 'profile_picture', 'phone')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Location'), {'fields': ('location', 'timezone')}),
        (_('Others'), {'fields': ('about_me', 'bio_me', 'short_me')})
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('_username', 'password1', 'password2')}),
        (_('Personal info'), {'fields': ('short_name', 'full_name', 'email', 'profile_picture', 'phone')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Location'), {'fields': ('location', 'timezone')}),
        (_('Others'), {'fields': ('about_me', 'bio_me', 'short_me')})
    )
    add_form = UserAddForm
    list_display = (
        'email', 'short_name', 'full_name',
        'location', 'slug',
        'date_joined',
        'is_superuser', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('short_name', 'full_name', 'email', 'location')
    ordering = ('_username',)
    filter_horizontal = ('groups', 'user_permissions',)


@admin.register(models.EmailAddress)
class EmailAddressAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'email', 'verified_at',
        'is_primary', 'type_email',
    )
    list_filter = ('type_email', 'is_primary',)
    search_fields = ('user__short_name', 'user__full_name', 'user__email',)
    ordering = ('email',)
