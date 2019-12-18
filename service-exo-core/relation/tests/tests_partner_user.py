from django.test import TestCase

from partner.faker_factories import FakePartnerFactory
from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from ..faker_factories import FakePartnerUserRoleFactory
from ..models import PartnerUserRole
from ..conf import settings


class PartnerUserRoleTest(TestCase):

    def setUp(self):
        super().setUp()
        self.partner = FakePartnerFactory.create()
        self.user1 = FakeUserFactory.create(is_active=True)
        self.user2 = FakeUserFactory.create(is_active=True)
        self.user3 = FakeUserFactory.create(is_active=True)

        self.role1 = FakePartnerUserRoleFactory.create(
            partner=self.partner,
            user=self.user1,
        )
        self.role2 = FakePartnerUserRoleFactory.create(
            partner=self.partner,
            user=self.user2,
        )

    def test_objects_manager(self):
        count = PartnerUserRole.objects.all().count()
        self.assertEqual(count, 2)

    def test_filter_actives(self):
        self.role1.status = settings.RELATION_ROLE_CH_ACTIVE
        self.role1.save()
        self.role2.status = settings.RELATION_ROLE_CH_INACTIVE
        self.role2.save()
        count = PartnerUserRole.objects.actives().count()
        self.assertEqual(count, 1)

    def test_filter_by_user(self):
        self.assertEqual(PartnerUserRole.objects.filter_by_user(user=self.user1).count(), 1)
        self.assertEqual(PartnerUserRole.objects.filter_by_user(user=self.user3).count(), 0)

    def test_queryset_roles(self):
        roles = PartnerUserRole.objects.filter(
            partner=self.partner,
        ).filter_by_user(
            user=self.user1,
        )
        self.assertEqual(len(roles), 1)

    def test_partner_users_manager(self):
        self.assertEqual(self.partner.users_roles.filter_by_user(self.user1).count(), 1)
