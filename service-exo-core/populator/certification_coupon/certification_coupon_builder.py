from django.conf import settings

from populate.populator.builder import Builder
from populate.populator.common.helpers import find_tuple_values

from exo_certification.models import Coupon, ExOCertification


class CertificationCouponBuilder(Builder):

    def create_object(self):
        type = find_tuple_values(
            settings.EXO_CERTIFICATION_COUPON_CH_TYPES,
            self.data.get('type'))[0]

        certification = ExOCertification.objects.get(
            level=self.data.get('certification')
        )

        owner = self.data.get('owner', None)
        if owner:
            owner = owner.user

        return Coupon.objects.create(
            code=self.data.get('code'),
            certification=certification,
            expiry_date=self.data.get('expiry_date', None),
            max_uses=self.data.get('max_uses', 10),
            uses=self.data.get('uses', 0),
            discount=self.data.get('discount'),
            type=type,
            owner=owner,
            fixed_email=self.data.get('fixed_email', None),
            comment=self.data.get('comment', None),
        )
