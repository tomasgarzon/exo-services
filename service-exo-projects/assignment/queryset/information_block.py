from django.db import models


class InformationBlockQuerySet(models.QuerySet):

    def filter_by_type(self, type):
        return self.filter(type=type)
