from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import (
    SuperUserTestMixin, UserTestMixin
)

from consultant.faker_factories import FakeConsultantFactory
from industry.models import Industry
from exo_attributes.models import ExOAttribute


class ConsultantManagerTest(
        UserTestMixin,
        SuperUserTestMixin,
        DjangoRestFrameworkTestCase
):

    def setUp(self):
        self.create_user()
        self.create_superuser()
        self.consultant = FakeConsultantFactory.create()

    def test_create_industries(self):
        industry1 = Industry.objects.all()[0]
        industry2 = Industry.objects.all()[1]

        self.consultant.industries.create(
            level=3,
            industry=industry1,
        )
        self.consultant.industries.create(
            level=1,
            industry=industry2,
        )

        self.assertEqual(
            self.consultant.industries.highest_level().count(),
            1,
        )

    def test_create_attributes(self):
        attr1 = ExOAttribute.objects.all()[0]
        attr2 = ExOAttribute.objects.all()[1]

        self.consultant.exo_attributes.create(
            level=5,
            exo_attribute=attr1,
        )
        self.consultant.exo_attributes.create(
            level=3,
            exo_attribute=attr2,
        )

        self.assertEqual(
            self.consultant.exo_attributes.highest_level().count(),
            1,
        )
