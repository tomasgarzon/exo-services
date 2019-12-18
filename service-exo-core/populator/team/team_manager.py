from singleton_decorator import singleton

from team.models import Team

from populate.populator.manager import Manager
from .team_builder import TeamBuilder


@singleton
class TeamManager(Manager):

    model = Team
    attribute = 'name'
    builder = TeamBuilder
    files_path = '/team/files/'
