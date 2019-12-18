# -*- coding: utf-8 -*-
import shutil
import tempfile

from django.conf import settings
from django.test.runner import DiscoverRunner
from django.core import mail
from django.core.mail import EmailMessage

from mock import patch
from email.mime.base import MIMEBase

from .pytest import bootstrap


class TempMediaMixin(object):

    def setup_test_environment(self, **kwargs):
        # Create temp directory and update MEDIA_ROOT and default storage.
        super().setup_test_environment(**kwargs)
        settings._original_media_root = settings.MEDIA_ROOT
        settings._original_file_storage = settings.DEFAULT_FILE_STORAGE
        self._temp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._temp_media
        settings.DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

    def teardown_test_environment(self, **kwargs):
        # Delete temp storage.
        super().teardown_test_environment(**kwargs)
        shutil.rmtree(self._temp_media, ignore_errors=True)
        settings.MEDIA_ROOT = settings._original_media_root
        del settings._original_media_root
        settings.DEFAULT_FILE_STORAGE = settings._original_file_storage
        del settings._original_file_storage


class LocalEmailMixin:
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        self.configure_mails()

    def teardown_test_environment(self, **kwargs):
        # Delete temp storage.
        super().teardown_test_environment(**kwargs)
        self.unconfigure_mails()

    def configure_mails(self):
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
        mail._original_email_backend = settings.EMAIL_BACKEND
        mail.outbox = []
        self.mail_patcher = patch(
            'utils.mail.handlers.mail_handler.send_mail',
            side_effect=self.get_send_mail_return_value)
        self.mock_mail = self.mail_patcher.start()

    def unconfigure_mails(self):
        mail.outbox = []
        self.mail_patcher.stop()

    def get_send_mail_return_value(self, *args, **kwargs):
        subject = kwargs.get('subject', '')
        from_email = kwargs.get('from_email', settings.MAIL_FROM_EMAIL)
        bcc = kwargs.get('bcc')
        cc = kwargs.get('cc')
        reply_to = kwargs.get('reply_to', [])
        files_attachment = kwargs.get('attachments', [])
        mail = EmailMessage(
            subject=subject,
            bcc=bcc,
            cc=cc,
            body=str(kwargs),
            from_email=from_email,
            to=kwargs.get('recipients'),
            reply_to=reply_to,
        )
        mail.content_subtype = 'html'

        for file_tmp in files_attachment:
            if isinstance(file_tmp, MIMEBase):
                mail.attach(file_tmp)
            else:
                try:
                    mail.attach(file_tmp.name, file_tmp.read(), file_tmp.content_type)
                except:  # noqa
                    mail.attach_file(file_tmp)
        mail.send()


class RunnerSetupMixin(LocalEmailMixin):

    def setup_test_environment(self, **kwargs):
        assert settings.TEST_MODE
        bootstrap.celery_fix()
        super().setup_test_environment(**kwargs)


class TestRunnerMixin(
        RunnerSetupMixin,
        TempMediaMixin,
        LocalEmailMixin,
        DiscoverRunner):
    pass
