from django.db import models


class UserMicroLearningQueryset(models.QuerySet):

    def filter_by_user(self, user):
        return self.filter(user=user)

    def filter_by_step(self, step):
        return self.filter(microlearning__step_stream__step=step)

    def filter_by_team_user(self, project, user):
        return self.filter(
            user__teams=user.teams.filter_by_project(project).first(),
        )

    def get_average(self):
        return self.aggregate(score_avg=models.Avg('score')).get('score_avg')

    def filter_by_team(self, team):
        return self.filter(user__teams=team)
