from django.core.management import call_command
from celery import Task


class InstrumentationTask(Task):
    name = 'InstrumentationTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        call_command('instrumentation')
