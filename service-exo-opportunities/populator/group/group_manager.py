from singleton_decorator import singleton

from opportunities.models import OpportunityGroup

from populate.populator.manager import Manager
from .group_builder import GroupBuilder


@singleton
class GroupManager(Manager):
    model = OpportunityGroup
    attribute = 'uuid'
    builder = GroupBuilder
    files_path = '/group/files/'
