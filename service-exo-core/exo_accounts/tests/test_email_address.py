from django.utils import timezone

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core import mail

from mock import patch

from ..test_mixins.faker_factories import FakeUserFactory
from .. import models

from utils.faker_factory import faker


class EmailAddressTest(TestCase):

    def test_create_user(self):
        user_email = faker.email().upper()
        user_pwd = faker.text()
        user = get_user_model().objects.create_user(
            email=user_email,
            password=user_pwd, short_name=faker.first_name())
        self.assertTrue(user.emailaddress_set.all().count() > 0)
        self.assertTrue(user.emailaddress_set.all()[0].is_verified)
        self.assertEqual(user.email, user_email.lower())

    @patch.object(models.EmailAddress, 'send_verification')
    def test_add_email_pending(self, mock_send_verification):
        # PREPARE DATA
        user = FakeUserFactory.create()

        # DO ACTION
        email_address = user.add_email_address(faker.email().upper())

        # ASSERTS
        self.assertEquals(40, len(email_address.verif_key))
        self.assertEqual(user.emailaddress_set.all().count(), 2)
        self.assertEqual(user.emailaddress_set.filter(verified_at__isnull=True).count(), 1)
        self.assertTrue(mock_send_verification.called)

    @patch.object(models.User, 'delete_platform_language_from_redis')
    @patch.object(models.EmailAddress, 'send_verification')
    def test_set_new_primary_flag_should_update_redis_language(
            self, mock_send_verification, mock_redis_language):
        # PREPARE DATA
        user = FakeUserFactory.create()
        email_address = user.add_email_address(faker.email().upper())

        # DO ACTION
        email_address._set_primary_flags()

        # ASSERTS
        user.refresh_from_db()
        self.assertEqual(mock_redis_language.call_count, 1)

    @patch.object(models.EmailAddress, 'send_verification')
    def test_set_new_primary_email(self, mock_send_verification):
        # PREPARE DATA
        user = FakeUserFactory.create()
        previous_email = user.email
        email_address = user.add_email_address(faker.email().upper())

        # DO ACTION
        email_address.set_primary()

        # ASSERTS
        user.refresh_from_db()
        self.assertEqual(user.email, email_address.email)
        self.assertEqual(user.email.lower(), email_address.email)
        self.assertEqual(user.emailaddress_set.get(is_primary=False).email,
                         previous_email)

    @patch.object(models.EmailAddress, 'send_verification')
    def test_remove_email(self, mock_send_verification):
        # PREPARE DATA
        user = FakeUserFactory.create()
        previous_email = user.email
        email_address = user.add_email_address(faker.email())
        email_address.set_primary()

        # DO ACTION
        email_address.delete()

        # ASSERTS
        self.assertEqual(user.email, previous_email)

    @patch.object(models.EmailAddress, 'send_verification')
    def test_authentication_with_new_email_pending(self, mock_send_verification):
        # PREPARE DATA
        client = Client()
        user = FakeUserFactory.create(is_active=True)

        # DO ACTIONS
        email_address = user.add_email_address(faker.email())

        # ASSERTS
        self.assertIsNone(email_address.verified_at)
        self.assertFalse(client.login(username=email_address.email,
                                      password=user.short_name))

    @patch.object(models.EmailAddress, 'send_verification')
    def test_authentication_with_new_primary_email_activated(self, mock_send_verification):
        # PREPARE DATA
        client = Client()

        user = FakeUserFactory.create(is_active=True)
        previous_email = user.email
        email_address = user.add_email_address(faker.email())

        # DO ACTIONS
        email_address.set_primary()

        # ASSERTS
        self.assertTrue(client.login(username=email_address.email,
                                     password=user.short_name))
        self.assertTrue(client.login(username=previous_email,
                                     password=user.short_name))

    @patch.object(models.EmailAddress, 'send_verification')
    def test_authentication_with_new_not_primary_email_activated(self, mock_send_verification):
        # PREPARE DATA
        client = Client()
        user = FakeUserFactory.create(is_active=True)

        # DO ACTIONS
        email_address = user.add_email_address(faker.email(), True)

        # ASSERTS
        self.assertIsNotNone(email_address.verified_at)
        self.assertTrue(client.login(username=email_address.email,
                                     password=user.short_name))

    @patch.object(models.EmailAddress, 'send_verification')
    def test_change_email(self, mock_send_verification):
        user_email = faker.email()
        user_pwd = faker.text()
        user = get_user_model().objects.create_user(
            email=user_email,
            password=user_pwd, short_name=faker.first_name())
        response = models.EmailAddress.objects.check_email(user, user_email)
        self.assertTrue(response[0])
        user_email2 = faker.email()
        email_address = models.EmailAddress.objects.add_email(user, user_email2)
        response = models.EmailAddress.objects.check_email(user, user_email2)
        self.assertFalse(response[0])
        self.assertEqual(
            response[1],
            settings.EXO_ACCOUNTS_VALIDATION_CHOICES_NOT_VERIFIED)
        email_address.verified_at = timezone.now()
        email_address.save()
        user.refresh_from_db()
        self.assertEqual(user.email, user_email)
        response = models.EmailAddress.objects.check_email(user, user_email2)
        self.assertTrue(response[0])
        self.assertEqual(
            response[1],
            settings.EXO_ACCOUNTS_VALIDATION_CHOICES_VERIFIED)

        other_email = faker.email()
        get_user_model().objects.create_user(
            email=other_email,
            password=user_pwd, short_name=faker.first_name())
        response = models.EmailAddress.objects.check_email(user, other_email)
        self.assertFalse(response[0])
        self.assertEqual(
            response[1],
            settings.EXO_ACCOUNTS_VALIDATION_CHOICES_OTHER_USER)
        response = models.EmailAddress.objects.check_email(user, faker.email())
        self.assertTrue(response[0])
        self.assertEqual(
            response[1],
            settings.EXO_ACCOUNTS_VALIDATION_CHOICES_PENDING)

    @patch.object(models.EmailAddress, 'send_verification')
    def test_change_unused_email(self, mock_send_verification):
        admin_user = FakeUserFactory.create(
            is_superuser=True,
            is_active=True)
        user_email = faker.email()
        user_pwd = faker.text()
        user = get_user_model().objects.create_user(
            email=user_email,
            password=user_pwd, short_name=faker.first_name())
        unused_email = faker.email()
        status, _ = models.EmailAddress.objects.change_user_email(
            admin_user, user, unused_email)
        self.assertTrue(status)
        user.refresh_from_db()
        self.assertEqual(user.email, unused_email)
        self.assertFalse(mock_send_verification.called)
        unused_email2 = faker.email()
        status, _ = models.EmailAddress.objects.change_user_email(
            user, user, unused_email2)
        self.assertTrue(status)
        user.refresh_from_db()
        self.assertEqual(user.email, unused_email)
        self.assertFalse(
            models.EmailAddress.objects.get(
                user=user, email=unused_email2).is_verified)
        self.assertTrue(mock_send_verification.called)

    @patch.object(models.EmailAddress, 'send_verification')
    def test_change_previous_used_email(self, mock_send_verification):
        admin_user = FakeUserFactory.create(
            is_superuser=True,
            is_active=True)
        user_email = faker.email()
        user_pwd = faker.text()
        user = get_user_model().objects.create_user(
            email=user_email,
            password=user_pwd, short_name=faker.first_name())
        unused_email = faker.email()
        email = models.EmailAddress.objects.create(user=user, email=unused_email)
        self.assertFalse(email.is_verified)
        self.assertEqual(user.email, user_email)
        # own user
        status, _ = models.EmailAddress.objects.change_user_email(
            user, user, unused_email)
        self.assertFalse(status)
        user.refresh_from_db()
        self.assertEqual(user.email, user_email)
        self.assertTrue(mock_send_verification.called)
        mock_send_verification.reset_mock()
        # admin user
        status, _ = models.EmailAddress.objects.change_user_email(
            admin_user, user, unused_email)
        self.assertTrue(status)
        user.refresh_from_db()
        self.assertEqual(user.email, unused_email)
        self.assertFalse(mock_send_verification.called)

        # Return a previous email already verified
        status, _ = models.EmailAddress.objects.change_user_email(
            user, user, user_email)
        self.assertTrue(status)
        user.refresh_from_db()
        self.assertEqual(user.email, user_email)
        self.assertFalse(mock_send_verification.called)

    def test_add_email_address_verified(self):
        user = FakeUserFactory.create()
        user.add_email_address(faker.email(), True)
        self.assertEqual(len(mail.outbox), 0)

    def test_add_user_email(self):
        user = FakeUserFactory.create()
        previous_email = user.email
        models.EmailAddress.objects.add_user_email(user, faker.email().upper())
        # User has to have 2 email address, both verified
        self.assertEqual(user.emailaddress_set.all().count(), 2)
        self.assertEqual(user.emailaddress_set.filter(verified_at__isnull=True).count(), 0)
        user2 = FakeUserFactory.create()
        status = models.EmailAddress.objects.add_user_email(user2, previous_email)
        # add an email used by other user
        self.assertFalse(status)
        # add a new email address pending of verified
        new_email = faker.email()
        user.add_email_address(new_email)
        status = models.EmailAddress.objects.add_user_email(user, new_email)
        # has to have 3 email verified
        self.assertTrue(status)
        self.assertEqual(user.emailaddress_set.all().count(), 3)
        self.assertEqual(user.emailaddress_set.filter(verified_at__isnull=True).count(), 0)
        user.refresh_from_db()
        # has to have the same email that he was created
        self.assertEqual(previous_email, user.email)
