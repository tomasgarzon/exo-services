from django.db import models


class CategoryQueryset(models.QuerySet):

    def filter_by_name(self, name):
        return self.filter(name=name)
