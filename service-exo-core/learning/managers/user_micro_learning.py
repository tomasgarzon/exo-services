from django.db import models

from ..querysets.user_microlearning import UserMicroLearningQueryset


class UserMicroLearningManager(models.Manager):
    queryset_class = UserMicroLearningQueryset

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user)

    def filter_by_team_user(self, project, user):
        return self.get_queryset().filter_by_team_user(project, user)

    def filter_by_team(self, team):
        return self.get_queryset().filter_by_team(team)
