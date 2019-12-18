from appconf import AppConf

from django.conf import settings

assert settings


class MailerConf(AppConf):

    FROM_EMAIL = 'OpenExO <hello@openexo.com>'
    REPLY_TO = 'support@openexo.com'
    INACTIVE_MAILS = ()
    CATEGORY_HEADER_KEY = 'ExOMail-Category'

    ERROR_MESAGE_SUBJECT = '[Django]'
    TEST_MESSAGE_SUBJECT = 'Test'

    LOG_ACTIONS_SENT = 'R'
    LOG_ACTIONS_STORED = 'S'
    LOG_ACTIONS_FAILED = 'F'

    LOG_ACTIONS_DEFAULT = LOG_ACTIONS_STORED

    LOG_ACTIONS_CHOICES = (
        (LOG_ACTIONS_STORED, 'Stored'),
        (LOG_ACTIONS_SENT, 'Sent'),
        (LOG_ACTIONS_FAILED, 'Failed'),
    )

    NOTIFY_WEBHOOK_STATUS_OK = 'Sent'
