from django.conf import settings

from .user_microlearning import UserMicroLearning


class MicroLearningAverage:
    # Old socket version
    user_avg = None
    team_avg = None
    user_project_avg = None
    team_project_avg = None

    # New Socket version
    all_team_avg = None
    users_score = None

    project = None
    team = None
    user = None
    step = None
    step_stream = None

    def __init__(self, step_stream, user, team=None):
        self.project = step_stream.step.project
        self.team = team
        self.user = user
        self.step = step_stream.step
        self.step_stream = step_stream
        self.users_score = []

        try:
            if self.user:
                self.user_avg = round(self.get_user_score(
                    step_stream, self.user), 1)
        except TypeError:
            self.user_avg = -1

        try:
            if not self.team:
                raise TypeError('Not team')
            self.team_avg = round(self.get_team_score(step_stream) or 0, 1)
            self.all_team_avg = round(self.get_team_score(step_stream, False) or 0, 1)

            for team_member in self.team.participants:
                user_score = self.get_user_score(step_stream, team_member) or -1
                self.users_score.append(round(user_score, 1))

        except TypeError:
            pass

        try:
            if self.user:
                self.user_project_avg = int(round(
                    self.get_user_project_score(self.user)))
        except TypeError:
            pass

        try:
            if not self.team:
                raise TypeError('Not team')
            self.team_project_avg = int(round(
                self.get_team_project_score(step_stream) or 0))
        except TypeError:
            pass

    def get_user_score(self, step_stream, user):
        return UserMicroLearning.objects.filter(
            microlearning__step_stream=step_stream,
        ).filter_by_user(user).get_average()

    def get_team_score(self, step_stream, relative_average=True):
        """
        Type of avergae availables are:
        - Relative average [relative_average=True]:
            which means, do not take care for unanswered `UserMicroLearning`
        - Absolute average [relative_average=False]:
            which means, count as 0 those unanswered `UserMicroLearning`
        """
        team_score = None
        user_microlearning_responses = UserMicroLearning.objects.filter(
            microlearning__step_stream=step_stream
        ).filter_by_team(self.get_team())

        if relative_average:
            team_score = user_microlearning_responses.get_average()
        else:
            responses = list(user_microlearning_responses.filter(
                status=settings.LEARNING_USER_MICROLEARNING_STATUS_DONE,
            ).values_list('score', flat=True))
            unanswered_items = self.get_team().participants.count() - len(responses)

            scores = responses + [0 for _ in range(unanswered_items)]
            team_score = sum(scores) / len(scores or 1)

        return team_score

    def get_user_project_score(self, user):
        return UserMicroLearning.objects.filter_by_user(
            user,
        ).get_average()

    def get_team_project_score(self, step_stream):
        return UserMicroLearning.objects.filter_by_team(
            self.get_team()).get_average()

    def get_project(self):
        return self.project

    def get_user(self):
        return self.user

    def get_team(self):
        return self.team

    def get_step(self):
        return self.step

    def get_stream(self):
        return self.step_stream.stream

    def serialize(self):
        return {
            'user': self.user_avg,
            'team': self.team_avg,
            'userProject': self.user_project_avg,
            'teamProject': self.team_project_avg,
            'allTeamAvg': self.all_team_avg,
            'ratings': self.users_score,
        }
