from django.conf import settings
from django.test import TestCase

from exo_accounts.test_mixins import UserTestMixin
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from exo_certification.models import Coupon
from test_utils.test_case_mixins import SuperUserTestMixin

from ..faker_factories.coupon import FakeCouponFactory
from .test_mixins import ExOCertificationTestMixin
from ..helpers.payment import final_price_coupon


class ExOCertificationCouponActionsTestCase(
        UserTestMixin,
        SuperUserTestMixin,
        ExOCertificationTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()
        self.create_user()
        self.create_cohorts()

    def test_apply_coupon(self):
        # PREPARE DATA
        coupon = FakeCouponFactory.create(max_uses=5)

        # DO ACTION
        coupon.apply(self.user, raise_exceptions=False)

        # ASSERTS
        updated_coupon = Coupon.objects.get(pk=coupon.pk)
        self.assertTrue(updated_coupon.is_available)
        self.assertEquals(updated_coupon.uses, 1)
        self.assertEqual(updated_coupon.logs.count(), 1)

    def test_apply_not_valid_coupon(self):
        # PREPARE DATA
        coupon = FakeCouponFactory.create(
            max_uses=5,
            uses=5,
        )

        # DO ACTION
        result = coupon.apply(self.user, raise_exceptions=False)
        updated_coupon = Coupon.objects.get(pk=coupon.pk)

        # ASSERTS
        self.assertFalse(result)
        self.assertFalse(updated_coupon.is_available)
        self.assertEquals(coupon.uses, coupon.max_uses)
        self.assertEqual(updated_coupon.logs.count(), 0)

    def test_coupon_max_uses(self):
        # PREPARE DATA
        coupon = FakeCouponFactory.create(
            max_uses=2,
            uses=0,
        )
        users = FakeUserFactory.create_batch(size=2)
        for user in users:
            coupon.apply(user)

        # DO ACTION
        result = coupon.apply(self.user, raise_exceptions=False)
        updated_coupon = Coupon.objects.get(pk=coupon.pk)

        # ASSERTS
        self.assertFalse(result)
        self.assertFalse(updated_coupon.is_available)
        self.assertEquals(coupon.uses, coupon.max_uses)

    def test_coupon_for_user(self):
        # PREPARE DATA
        user = FakeUserFactory.create()
        coupon = FakeCouponFactory.create(
            max_uses=2,
            fixed_email=user.email,
        )

        # DO ACTION
        result_other = coupon.check_for_user(self.user)
        result_user = coupon.check_for_user(user)

        # ASSERTS
        self.assertFalse(result_other)
        self.assertTrue(result_user)

    def test_can_use_coupon_success(self):
        # PREPARE DATA
        coupon = FakeCouponFactory.create(
            max_uses=2,
            type=settings.EXO_CERTIFICATION_COUPON_TYPES_CH_PERCENT,
            certification=self.cohort_lvl_2.certification,
            discount=20,
        )

        # DO ACTION
        can_use = coupon.can_use_coupon(
            certification=self.cohort_lvl_2.certification,
            raise_exceptions=False,
        )

        # ASSERTS
        self.assertTrue(can_use)

    def test_can_use_coupon_fail(self):
        # PREPARE DATA
        coupon = FakeCouponFactory.create(
            max_uses=2,
            type=settings.EXO_CERTIFICATION_COUPON_TYPES_CH_PERCENT,
            certification=self.cohort_lvl_3.certification,
            discount=20,
        )

        # DO ACTION
        can_use = coupon.can_use_coupon(
            certification=self.cohort_lvl_2.certification,
            raise_exceptions=False,
        )

        # ASSERTS
        self.assertFalse(can_use)

    def test_coupon_discount_percentage(self):
        # PREPARE DATA
        coupon = FakeCouponFactory.create(
            max_uses=2,
            type=settings.EXO_CERTIFICATION_COUPON_TYPES_CH_PERCENT,
            certification=self.cohort_lvl_2.certification,
            discount=20,
        )

        # DO ACTION
        price = final_price_coupon(coupon.code, self.cohort_lvl_2)

        # ASSERTS
        self.assertEqual(
            price,
            1200)

    def test_coupon_discount_fixed(self):
        # PREPARE DATA
        coupon = FakeCouponFactory.create(
            max_uses=2,
            type=settings.EXO_CERTIFICATION_COUPON_TYPES_CH_AMOUNT,
            certification=self.cohort_lvl_2.certification,
            discount=500,
        )

        # DO ACTION
        price = final_price_coupon(coupon.code, self.cohort_lvl_2)

        # ASSERTS
        self.assertEqual(
            price,
            1000)
