# -*- coding: utf-8 -*-
"""
License boilerplate should be used here.
"""
# django imports
from django.apps import AppConfig

# app imports
from . import mailviews
from .discover import discover_mailviews
from .handlers import mail_handler


class MailConfig(AppConfig):
    name = 'mail'

    def ready(self):
        super(MailConfig, self).ready()

        # Register mails
        for mailview_name, mailview in discover_mailviews():
            setattr(mailviews, mailview_name, mailview)
            mail_handler.register(mailview)
