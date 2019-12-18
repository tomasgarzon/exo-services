from django.conf import settings


class TeamMemberManager:
    members = []

    def __init__(self, team):
        for user in team.team_members.all():
            team_member = TeamMember(team, user)
            self.members.append(team_member)

    def get_by_user(self, user):
        team_members = list(filter(lambda x: x.user == user, self.members))
        if team_members:
            return team_members[0]
        return None


class TeamMember:

    def __init__(self, team, user):
        self.team = team
        self.user = user

    def get_or_create_feedback_for_step(self, step):
        user_feedback = None
        created = False
        stream = self.team.stream
        step_stream = step.streams.get(stream=stream)
        feedback = step_stream.typeform_feedback
        if feedback.exists():
            step_feedback = feedback.first()
            user_feedback, created = step_feedback.responses.get_or_create(
                user=self.user,
                defaults={'status': settings.TYPEFORM_FEEDBACK_USER_FEEDBACK_STATUS_PENDING},
            )
        return user_feedback, created
