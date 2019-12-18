from singleton_decorator import singleton

from exo_certification.models import Coupon

from populate.populator.manager import Manager
from .certification_coupon_builder import CertificationCouponBuilder


@singleton
class CertificationCouponManager(Manager):
    model = Coupon
    attribute = 'code'
    builder = CertificationCouponBuilder
    files_path = '/certification_coupon/files/'

    def get_object(self, value):
        return super().get_object(value.upper())
