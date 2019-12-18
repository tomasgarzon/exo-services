from django.db.models import Manager

from ..queryset.survey import SurveyQueryset


class SurveyManager(Manager):
    queryset_class = SurveyQueryset

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)
