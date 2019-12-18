from django.db import models


class StepStreamQuerySet(models.QuerySet):

    def filter_by_step(self, step):
        return self.filter(step=step)

    def filter_by_stream(self, stream):
        return self.filter(stream=stream)
