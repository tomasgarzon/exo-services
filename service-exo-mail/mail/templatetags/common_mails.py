# -*- coding: utf-8 -*-
"""
License boilerplate should be used here.
"""
# django imports
from django.conf import settings
from django import template

register = template.Library()


@register.simple_tag
def server_asset():
    return '{}/static/'.format(settings.EXOLEVER_HOST)
