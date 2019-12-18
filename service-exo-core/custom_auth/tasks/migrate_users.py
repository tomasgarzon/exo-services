from django.core.management import call_command
from celery import Task


class MigrateUserTask(Task):
    name = 'MigrateUserTask'
    ignore_results = True

    def run(self, *args, **kwargs):
        call_command('syncronize_users')
