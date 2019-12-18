from django.test import TestCase
from django.core.mail import get_connection


class MailSendTest(TestCase):

    def test_real_server_config(self):
        connection = get_connection(backend='django.core.mail.backends.smtp.EmailBackend')
        self.assertTrue(connection.open())
        connection.close()
