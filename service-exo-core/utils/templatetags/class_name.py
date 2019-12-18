from django import template


register = template.Library()


@register.filter(name='verbose_name')
def class_name(django_class):
    return django_class.__class__._meta.verbose_name if django_class else ''


@register.filter(name='verbose_name_plural')
def verbose_name_plural(django_class):
    return django_class.__class__._meta.verbose_name_plural if django_class else ''


@register.filter(name='fa_icon')
def fa_icon(verbose_name):
    FA_DICT = {
        'Task': 'fa-tasks',
    }
    FA_DEFAULT = 'fa-home'
    return FA_DICT.get(verbose_name, FA_DEFAULT)
