from django.test import TestCase
from django.contrib.auth import get_user, get_user_model
from django.urls import reverse

from exo_accounts.settings import MM
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from exo_messages.conf import settings
from exo_messages.models import Message
from utils.faker_factory import faker


User = get_user_model()


class InternalMessageTest(TestCase):

    def test_add_email(self):
        user = FakeUserFactory.create()
        email_address = user.add_email_address(faker.email().upper())
        self.assertEqual(
            Message.objects.filter_by_user(
                user).filter_by_code(settings.EXO_MESSAGES_CH_CODE_PENDING_EMAIL).count(),
            1)
        self.assertEqual(
            Message.objects.filter_by_user(
                user).filter(
                variables__pk=email_address.pk).count(),
            1)

    def test_validate_email(self):
        user = FakeUserFactory.create()
        email_address = user.add_email_address(faker.email().upper())
        url = reverse(
            MM.EMAIL_VERIFICATION_URL_VIEW_NAME,
            kwargs={
                'email_pk': email_address.pk,
                'verif_key': email_address.verif_key,
            },
        )
        self.client.get(url)
        email_address.refresh_from_db()
        user = get_user(self.client)
        self.assertTrue(email_address.is_verified)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(Message.objects.filter_by_user(
            user).filter(variables__pk=email_address.pk).count(), 1)
        self.assertEqual(Message.objects.filter_by_user(
            user).filter_by_code(settings.EXO_MESSAGES_CH_CODE_PENDING_EMAIL).count(), 0)
        self.assertEqual(Message.objects.filter_by_user(
            user).filter_by_code(settings.EXO_MESSAGES_CH_CODE_VALIDATED_EMAIL).count(), 1)
        self.assertEqual(Message.objects.filter_by_user(
            user).filter_by_code(settings.EXO_MESSAGES_CH_CODE_VALIDATED_EMAIL).already_read().count(), 1)

    def test_validate_email_not_valid_email_pk(self):
        user = FakeUserFactory.create()
        email_address = user.add_email_address(faker.email().upper())
        url = reverse(
            MM.EMAIL_VERIFICATION_URL_VIEW_NAME,
            kwargs={
                'email_pk': 999999999,
                'verif_key': email_address.verif_key,
            },
        )
        response = self.client.get(url)
        self.assertTrue(response.status_code, 404)

    def test_messages_delete_email(self):
        user = FakeUserFactory.create(password='123456')
        email_address = user.add_email_address(faker.email().upper())
        self.assertEqual(Message.objects.filter_by_user(user).count(), 1)
        email_address.delete()
        self.assertEqual(Message.objects.filter_by_user(user).count(), 0)
