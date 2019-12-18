import re

from django.conf import settings

from functools import reduce

from utils.mail import handlers
from utils.mail.mails_mixin import EmailMixin


def _extract_params(string_source):
    """
        Will look for pattern like '%(foo_bar.foo.bar)s'
    """
    exp = '%\((.[a-zA-Z\.\_]*?)\)s'  # noqa
    regex = re.compile(exp)
    return regex.findall(string_source)


def _compose_string(string_to_compose, **kwargs):
    params = {}
    notification_tpl = kwargs.get('notification_tpl', None)
    if notification_tpl:
        subject_params = _extract_params(string_to_compose)
        for parameter in subject_params:
            param = kwargs.get(parameter.split('.')[0])
            param = reduce(getattr, parameter.split('.')[1:], param)
            params[parameter] = param
    return string_to_compose % params


class ProcessStepEmailMixin(EmailMixin):

    def _build_parameters(
        self, notification_tpl, step_name, user_from,
        subject=None, body_mail=None,
    ):

        recipients = self.get_group_destinataries(settings.REGISTRATION_GROUP_NAME)

        kwargs = {'mail_name': notification_tpl}
        kwargs['recipients'] = recipients
        kwargs['name'] = user_from.get_full_name()
        kwargs['email'] = user_from.email
        kwargs['step_name'] = step_name
        if subject:
            subject_args = {}
            subject_args['subject'] = _compose_string(subject, **locals())
            kwargs['subject_args'] = subject_args
        if body_mail:
            kwargs['body_mail'] = _compose_string(body_mail, **locals())

        return kwargs

    def _send_email_step_ok(self, template, user_from, *args, **kwargs):
        parameters = self._build_parameters(
            notification_tpl=template.email_tpl.email_ok,
            step_name=template.name,
            user_from=user_from,
            subject=template.email_tpl.email_ok_subject or None,
            body_mail=template.email_tpl.email_ok_body or None,
        )
        parameters.update(kwargs)
        parameters['template'] = parameters['mail_name']
        handlers.mail_handler.send_mail(**parameters)

    def _send_email_step_ko(self, template, user_from, *args, **kwargs):
        parameters = self._build_parameters(
            notification_tpl=template.email_tpl.email_ko,
            step_name=template.name,
            user_from=user_from,
            subject=template.email_tpl.email_ko_subject or None,
            body_mail=template.email_tpl.email_ko_body or None,
        )
        parameters.update(kwargs)
        parameters['template'] = parameters['mail_name']
        handlers.mail_handler.send_mail(**parameters)
