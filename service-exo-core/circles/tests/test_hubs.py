from django.test import TestCase

from actstream.models import following, followers

from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from consultant.faker_factories import FakeConsultantFactory
from relation.models import HubUser
from consultant.signals_define import consultant_post_activated
from test_utils.test_case_mixins import SuperUserTestMixin

from ..models import Circle
from ..conf import settings


class HubCircleTest(
        SuperUserTestMixin,
        TestCase):

    def setUp(self):
        self.create_superuser()

    def test_user_added_hub(self):
        # PREPARE DATA
        user = FakeUserFactory(is_active=True)
        circle = Circle.objects.first()

        # DO ACTION
        HubUser.objects.create(
            user=user,
            hub=circle.hub)

        # ASSERTS
        self.assertTrue(
            user.has_perm(
                settings.CIRCLES_PERMS_CREATE_POST,
                circle)
        )
        self.assertEqual(following(user, Circle), [circle])
        self.assertEqual(followers(circle), [user])

    def test_user_removed_hub(self):
        # PREPARE DATA
        user = FakeUserFactory(is_active=True)
        circle = Circle.objects.first()
        hubuser = HubUser.objects.create(
            user=user,
            hub=circle.hub)

        # DO ACTION
        hubuser.delete()

        # ASSERTS
        self.assertFalse(
            user.has_perm(
                settings.CIRCLES_PERMS_CREATE_POST,
                circle)
        )
        self.assertEqual(following(user, Circle), [])
        self.assertEqual(followers(circle), [])

    def test_consultant_circles(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()

        # DO ACTION
        consultant_post_activated.send(
            sender=consultant.__class__, consultant=consultant)

        # ASSERTS
        self.assertEqual(
            len(following(consultant.user, Circle)),
            len(settings.CIRCLES_FOR_CONSULTANTS),
        )

    def test_consultant_disabled_in_circles(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        circle = Circle.objects.get(name=settings.CIRCLES_ECOSYSTEM_NAME)
        consultant_post_activated.send(
            sender=consultant.__class__, consultant=consultant)
        circle = Circle.objects.first()
        HubUser.objects.create(
            user=consultant.user,
            hub=circle.hub)

        # DO ACTION
        consultant.disable(self.super_user)

        # ASSERTS
        self.assertEqual(following(consultant.user, Circle), [])
