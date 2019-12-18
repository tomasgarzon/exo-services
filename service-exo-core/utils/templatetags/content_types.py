# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
# Stdlib imports

# Core Django imports
from django import template

# Third-party app imports

# Realative imports of the 'app-name' package


register = template.Library()


@register.filter('content_type_id')
def get_content_type(obj):
    return ContentType.objects.get_for_model(obj).id


@register.simple_tag(name='content_type_id_by_model')
def get_content_type_id_by_model(model_name):
    [app_name, model_name] = model_name.split('.')
    return ContentType.objects.get(app_label=app_name, model=model_name).id
