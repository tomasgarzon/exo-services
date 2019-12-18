from singleton_decorator import singleton

from populate.populator.manager import Manager
from jobs.models import Job

from .jobs_builder import JobBuilder


@singleton
class JobsManager(Manager):
    model = Job
    attribute = 'uuid'
    builder = JobBuilder
    files_path = '/jobs/files/'
