from __future__ import unicode_literals

import logging
from inspect import ismethod

from django.urls import (
    reverse, resolve, NoReverseMatch,
    Resolver404
)
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_text
from django.db.models import Model
from django.conf import settings
from django import template


logger = logging.getLogger(__name__)

register = template.Library()

CONTEXT_KEY = 'DJANGO_BREADCRUMB_LINKS'


def build_links(context):
    links = []
    for (label, viewname, view_args, view_kwargs) in context[
            'request'
    ].META.get(CONTEXT_KEY, []):
        if isinstance(viewname, Model) and hasattr(
                viewname, 'get_absolute_url',
        ) and ismethod(
                viewname.get_absolute_url,
        ):
            url = viewname.get_absolute_url(*view_args, **view_kwargs)
        else:
            try:
                try:
                    # 'resolver_match' introduced in Django 1.5
                    current_app = context['request'].resolver_match.namespace
                except AttributeError:
                    try:
                        resolver_match = resolve(context['request'].path)
                        current_app = resolver_match.namespace
                    except Resolver404:
                        current_app = None
                url = reverse(
                    viewname=viewname, args=view_args,
                    kwargs=view_kwargs, current_app=current_app,
                )
            except NoReverseMatch:
                url = viewname
        links.append((url, smart_text(label) if label else label, viewname))
    return links


@register.simple_tag(takes_context=True)
def render_view_breadcrumbs(context, *args):
    """
    Render breadcrumbs html using bootstrap css classes.
    """
    if 'request' not in context:
        logger.error(
            'request object not found in context! Check if '
            "'django.core.context_processors.request' is in "
            'TEMPLATE_CONTEXT_PROCESSORS',
        )
        return ''

    if args:
        template_path = args[0]
    else:
        try:
            template_path = settings.BREADCRUMBS_TEMPLATE
        except AttributeError:
            template_path = 'django_bootstrap_breadcrumbs/bootstrap2.html'

    my_context = {}
    links = build_links(context)
    my_context['hide_breadcrumb'] = False
    if not links or context['user'].is_customer:
        my_context['hide_breadcrumb'] = True
    my_context['breadcrumbs'] = links
    my_context['breadcrumbs_total'] = len(links)
    return mark_safe(template.loader.render_to_string(
        template_path, context=my_context,
    ))
