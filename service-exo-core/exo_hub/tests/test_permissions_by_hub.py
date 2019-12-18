from django.conf import settings
from django.test import TestCase

from consultant.faker_factories import FakeConsultantFactory
from relation.signals_define import add_user_exo_hub, remove_user_exo_hub


class PermissionsByHubTest(TestCase):

    def test_adding_consultant_permissions(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(user__is_active=True)
        permissions_before = consultant.user.user_permissions.all().count()

        # DO ACTION
        add_user_exo_hub.send(
            sender=self.__class__,
            user=consultant.user,
            exo_hub_code=settings.EXO_HUB_CH_CONSULTANT,
        )

        # ASSERTS
        permissions_after = consultant.user.user_permissions.all().count()
        self.assertLess(permissions_before, permissions_after)

    def test_removing_consultant_permissions(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(user__is_active=True)
        add_user_exo_hub.send(
            sender=self.__class__,
            user=consultant.user,
            exo_hub_code=settings.EXO_HUB_CH_CONSULTANT,
        )
        permissions_before = consultant.user.user_permissions.all().count()

        # DO ACTION
        remove_user_exo_hub.send(
            sender=self.__class__,
            user=consultant.user,
            exo_hub_code=settings.EXO_HUB_CH_CONSULTANT,
        )

        # ASSERTS
        permissions_after = consultant.user.user_permissions.all().count()
        self.assertGreater(permissions_before, permissions_after)
