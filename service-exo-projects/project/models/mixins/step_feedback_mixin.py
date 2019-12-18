from django.conf import settings
from django.core.exceptions import ValidationError

from auth_uuid.utils.user_wrapper import UserWrapper

from utils.xlsx import XlsxWrapper


class StepFeedbackMixin:
    SHEET_TEAM = 'team'
    SHEET_COACH = 'coach'

    def can_download_report(self, user_from, raise_exceptions=True):
        is_valid = self.project.created_by == user_from or user_from.is_superuser

        if not is_valid and raise_exceptions:
            raise ValidationError("User can't download report")
        return is_valid

    def set_excel_columns(self, worksheet, sheet_name):

        styles = [
            ('A:A', 20),
            ('B:B', 40),
            ('C:C', 40),
            ('D:D', 40),
            ('E:E', 20),
            ('H:H', 20),
        ]

        columns = {
            'team': [
                ('A1', 'Client'),
                ('B1', 'Team'),
                ('C1', 'Coach'),
                ('D1', 'Participant'),
                ('E1', 'Week'),
                ('F1', 'Rating'),
                ('G1', 'Feedback'),
                ('H1', 'Comments'),
            ],
            'coach': [
                ('A1', 'Client'),
                ('B1', 'Team'),
                ('C1', 'Head Coach'),
                ('D1', 'Coach'),
                ('E1', 'Week'),
                ('F1', 'Rating'),
                ('G1', 'Feedback'),
                ('H1', 'Comments'),
            ]
        }

        for pos, value in styles:
            worksheet.set_column(pos, value)

        for pos, name in columns[sheet_name]:
            worksheet.write(pos, name)

    def write_data(self, worksheet, user_from, team_step, row, sheet_name):
        worksheet.write(row, 0, team_step.project.name)
        worksheet.write(row, 1, team_step.team.name)

        if sheet_name == self.SHEET_TEAM:
            coaches = team_step.team.coaches
            names = []
            for coach in coaches:
                names.append(UserWrapper(user=coach).get_full_name())
            worksheet.write(row, 2, ', '.join(names))
            worksheet.write(row, 3, UserWrapper(user=user_from).get_full_name())
        elif sheet_name == self.SHEET_COACH:
            names = []
            for user in self.project.users_with_admin_perm():
                names.append(UserWrapper(user=user).get_full_name())
            worksheet.write(row, 2, ', '.join(names))
            coaches = team_step.team.coaches
            names = []
            for coach in coaches:
                names.append(UserWrapper(user=coach).get_full_name())
            worksheet.write(row, 3, ', '.join(names))

        worksheet.write(row, 4, team_step.step.name)
        worksheet.write(row, 5, team_step.get_rating_for_user(user_from))

        user_feedback = team_step.get_feedback_for_user(user_from)
        worksheet.write(row, 6, user_feedback)

        last_feedback = team_step.get_last_action_feedback(
            user=user_from,
            verb=settings.TEAM_ACTION_COMMENT_WEEKLY,
        )
        worksheet.write(row, 7, last_feedback.description if last_feedback else '-')

    def create_coaches_raw_data(self, worksheet):
        self.set_excel_columns(worksheet, 'coach')
        row = 1
        steps = self.project.steps.filter(index__lte=self.index)

        for step in steps:
            for team in step.project.teams.all():
                team_step = step.teams.filter(team=team).first()

                if team_step:
                    coaches = team_step.team.coaches
                    for coach in coaches:
                        self.write_data(worksheet, coach, team_step, row, self.SHEET_COACH)
                        row += 1

    def create_team_raw_data(self, worksheet):
        self.set_excel_columns(worksheet, 'team')
        row = 1
        steps = self.project.steps.filter(index__lte=self.index)

        for step in steps:
            for team in step.project.teams.all():
                team_step = step.teams.filter(team=team).first()

                if team_step:
                    for member in team.participants:
                        self.write_data(worksheet, member, team_step, row, self.SHEET_TEAM)
                        row += 1

    def create_feedbacks_excel_report(self):
        filename = '{}-{}'.format(str(self.project.name), str(self.name))
        wrapper = XlsxWrapper(filename)

        worksheet = wrapper.create_worksheet('RAW DATA Team')
        self.create_team_raw_data(worksheet)

        worksheet = wrapper.create_worksheet('RAW DATA Coaches')
        self.create_coaches_raw_data(worksheet)

        wrapper.close()
        return wrapper
