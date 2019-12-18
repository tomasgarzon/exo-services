# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.apps import apps
from django.conf import settings

from utils.list import remove_element


class RecipientsHandler:

    def get_recipients_language(self, recipients):
        recipients_clear = remove_element(recipients, None)
        language_to_activate = settings.LANGUAGE_DEFAULT

        if recipients_clear:
            try:
                languages = get_user_model().objects.get_platform_languages(recipients_clear)
                language_to_activate = languages[0] if len(languages) == 1 else settings.LANGUAGE_DEFAULT
            except Exception as exc:  # noqa
                language_to_activate = settings.LANGUAGE_DEFAULT

        return language_to_activate

    def clear_recipients(self, config_param_name, recipients):
        if not config_param_name:
            return recipients

        ConfigParam = apps.get_model(app_label='account_config', model_name='ConfigParam')
        clean_recipients = []

        for email in recipients:
            try:
                user = get_user_model().objects.get(emailaddress__email=email)
            except get_user_model().DoesNotExist:
                clean_recipients.append(email)
                continue
            if not user.is_active:
                continue
            agent = user

            if user.is_consultant:
                agent = user.consultant

            config_param = ConfigParam.objects.get(name=config_param_name)

            try:
                value = config_param.get_value_for_agent(agent)
                if value:
                    clean_recipients.append(email)
            except ValueError:
                clean_recipients.append(email)

        return clean_recipients


recipients_handler = RecipientsHandler()
