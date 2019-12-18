from singleton_decorator import singleton

from opportunities.models import Opportunity

from populate.populator.manager import Manager
from .opportunity_builder import OpportunityBuilder


@singleton
class OpportunitiesManager(Manager):
    model = Opportunity
    attribute = 'uuid'
    builder = OpportunityBuilder
    files_path = '/opportunities/files/'
