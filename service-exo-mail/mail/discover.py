# -*- coding: utf-8 -*-
"""
License boilerplate should be used here.
"""
# python imports
import pkgutil
import inspect
import sys

from django.utils import six

from importlib import import_module

from .mails import BaseMailView
from .conf import settings
from . import mailviews as mailviews_pkg

APP = __name__.split('.', 1)[0]


def discover_mailview(badge):
    try:
        module = import_module('.mailviews.{}'.format(badge), APP)
    except ImportError as e:
        raise six.reraise(type(e), e, sys.exc_info()[2])
    else:
        member_classes = inspect.getmembers(module, inspect.isclass)
        models_classes = (
            member for member in member_classes
            if member[1].__module__.split('.')[-1] == badge and issubclass(member[1], BaseMailView)  # noqa
        )
        return models_classes


def discover_mailviews():
    badge_list = ()
    active_mails = [
        modname for importer, modname, ispkg in
        pkgutil.iter_modules(mailviews_pkg.__path__)
        if modname not in settings.MAIL_INACTIVE_MAILS
    ]

    for mail_module_name in active_mails:
        mail_class = discover_mailview(mail_module_name)
        badge_list += tuple(mail_class)

    return badge_list
