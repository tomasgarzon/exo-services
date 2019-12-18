from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from utils.test_mixin import UserTestMixin


class SignalsTestCase(UserTestMixin, TestCase):

    def test_post_migrate_signal(self):
        # PREPARE DATA
        User = get_user_model()
        ctype = ContentType.objects.get_for_model(User, for_concrete_model=False)
        perms = Permission.objects.filter(
            content_type=ctype).values_list('codename', flat=True)

        # ASSERTS
        for codename, _ in settings.AUTH_USER_ALL_PERMISSIONS:
            self.assertTrue(Permission.objects.filter(codename=codename).exists())
            self.assertIn(codename, perms)
