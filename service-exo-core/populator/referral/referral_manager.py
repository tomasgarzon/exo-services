from singleton_decorator import singleton
from populate.populator.manager import Manager

from referral.models import Campaign

from .referral_builder import ReferralBuilder


@singleton
class ReferralManager(Manager):
    model = Campaign
    attribute = 'name'
    builder = ReferralBuilder
    files_path = '/referral/files/'
