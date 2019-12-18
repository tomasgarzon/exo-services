from django import template

from ..conf import settings

register = template.Library()


@register.filter
def can_be_fixed(validation, user):
    if not validation.is_pending:
        return False

    if validation.validation_detail in settings.VALIDATION_ONLY_STAFF:
        return user.is_staff
    return True


@register.inclusion_tag('tags/validation_resume.html', takes_context=False)
def validation_resume(project):
    return {
        'warnings': project.validations.filter_by_validation_type_warning().filter_by_status_pending().count(),
        'errors': project.validations.filter_by_validation_type_error().filter_by_status_pending().count(),
    }
