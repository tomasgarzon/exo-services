# -*- coding: utf-8 -*-
import logging

from django.apps import apps
from django.shortcuts import render_to_response
from django.views.generic import TemplateView
from django.core import signing
from django.conf import settings

from utils.loader import dump_class

from . import sender

logger = logging.getLogger('service')


class BaseMailView(TemplateView):
    http_method_names = ['get']
    context = {}
    from_email = settings.MAIL_FROM_EMAIL
    from_name = settings.BRAND_NAME
    recipients = []
    mandatory_mail_args = []
    optional_mail_args = []
    attachments_args = []
    subject = None
    section = ''
    config_param = None

    def get_mandatory_mail_args(self):
        return self.mandatory_mail_args

    def validate_mandatory_mail_args(self, context):
        for arg in self.get_mandatory_mail_args():
            if arg not in context.keys():
                msg = 'Some mandatory attributes are not fulfilled args={arg}'.format(arg=arg)
                raise AttributeError(msg)
        return context

    def get_mock_data(self, optional=False):
        """
        Simulates a context for each mail. By default the super class
        returns an empty dictionary
        """
        data = {}

        if self._values:
            data = self._values

        return data

    def get_subject(self, **kwargs):
        return self.subject % kwargs

    def send_mail(
            self,
            mock_data=False,
            language_code='es',
            preview=False,
            bcc=None,
            cc=None,
            recipients=[],
            attachments=[],
            subject_args={},
            reply_to=[settings.MAIL_REPLY_TO],
            **kwargs):

        if mock_data:
            context = self.get_mock_data()
            context.update({'subject': self.subject})
        else:
            context = kwargs

        self.validate_mandatory_mail_args(context)

        subject = self.get_subject(**subject_args)
        context.update({'hash': self.build_hash(context)})
        context.update({'subject': subject})
        context.update({'preview': preview})

        message_rendered = render_to_response(
            self.template_name, context
        ).content

        if preview:
            return {
                'subject': subject,
                'body': message_rendered.decode('utf-8').replace('\n', ''),
            }
        else:
            if kwargs.get('from_email', None):
                from_email = kwargs['from_email']
            else:
                from_email = self.from_email

            sender.send_email(
                subject=subject,
                body=message_rendered.decode('utf-8'),
                from_email=from_email,
                to_email=recipients,
                files_attachment=attachments,
                reply=reply_to,
                bcc=bcc,
                cc=cc,
                category=kwargs['category'],
                notify_webhook=kwargs.get('notify_webhook', None),
            )

    def get_context_data(self, **kwargs):
        """
        Complete all the context necessary to fill the template
        """
        context = super(BaseMailView, self).get_context_data(**kwargs)
        self.context.update(context)

        if self._values:
            data = self._values
        else:
            data = self.get_mock_data()

        # Only for testing
        self.context.update(data)
        # example of dump_class(self)
        # 'mail.mailviews.invitation_consultant_project.InvitationConsultantProjectMailView'
        # we only need invitation_consultant_project
        self.context['hash'] = self.build_hash(data)
        self.validate_mandatory_mail_args(self.context)

        return self.context

    def get(self, request, **kwargs):
        self._values = kwargs
        return super().get(request)

    def build_hash(self, data):
        data['view_name'] = dump_class(self).split('.')[-2]
        return signing.dumps(data)

    # Related to async task and registered emails
    def freeze(self, **state):
        return state

    def prepare_email(self, recipients=[], **state):
        deserialized_keys = {}

        for key, value in state.iteritems():
            if key.startswith('model__'):
                value_list = value.split(',')
                key_name = value_list[0]
                app_label = value_list[1]
                object_name = value_list[2]
                pk = value_list[3]
                obj = apps.get_model(
                    app_label=app_label,
                    model_name=object_name,
                ).objects.get(pk=pk)
                deserialized_keys[key_name] = obj

        state.update(**deserialized_keys)
        self.send(recipients=recipients, **state)
