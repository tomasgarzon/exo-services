from django.conf import settings


VISIBLE_BY_DEFAULT = [settings.PROJECT_CH_CATEGORY_TRANSFORMATION]


def update_roles_by_category(project, queryset):
    visible = project.category in VISIBLE_BY_DEFAULT
    for value in queryset:
        value.visible = visible
        value.save(update_fields=['visible'])


def update_role_for_project_role(project_role_instance):
    project = project_role_instance.project
    project_role_instance.visible = project.category in VISIBLE_BY_DEFAULT
