from singleton_decorator import singleton

from populate.populator.manager import Manager

from project.models import Project

from .project_builder import ProjectBuilder


@singleton
class ProjectsManager(Manager):
    model = Project
    attribute = 'name'
    builder = ProjectBuilder
    files_path = '/projects/files/'
