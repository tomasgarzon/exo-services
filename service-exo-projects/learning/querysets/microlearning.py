from django.db import models


class MicrolearningQueryset(models.QuerySet):

    def filter_by_step(self, step):
        return self.filter(step_stream__step=step)
