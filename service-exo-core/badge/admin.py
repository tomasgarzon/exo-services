from django.contrib import admin

from .models import (
    Badge,
    UserBadge,
    UserBadgeActivity,
    UserBadgeJob,
    UserBadgeItem,
)


class BadgeAdmin(admin.ModelAdmin):
    list_filter = ('category', )
    list_display = ('code', 'category', 'order', 'created')


class UserBadgeAdmin(admin.ModelAdmin):
    search_fields = ('user__full_name', 'user__email')
    list_filter = ('badge__category', 'badge', )
    list_display = ('user', 'badge', 'num', 'created')


class UserBadgeActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'created')


class UserBadgeJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'created')


class UserBadgeItemAdmin(admin.ModelAdmin):
    search_fields = ('user_badge__user__full_name', 'user_badge__user__email')
    list_filter = ('user_badge__badge__category',)
    list_display = ('user_badge', 'name', 'date', 'created')


admin.site.register(Badge, BadgeAdmin)
admin.site.register(UserBadge, UserBadgeAdmin)
admin.site.register(UserBadgeActivity, UserBadgeActivityAdmin)
admin.site.register(UserBadgeJob, UserBadgeJobAdmin)
admin.site.register(UserBadgeItem, UserBadgeItemAdmin)
