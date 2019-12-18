from django.conf import settings

from utils.mail import handlers
from custom_auth.helpers import UserProfileWrapper


class QASessionMailMixin:

    def get_data_reminder(self):
        data = {
            'type_project': self.project.type_verbose_name,
            'project_name': self.project.name,
            'location': self.project.location,
            'timezone_utc': self.project.get_timezone_utc_relative(),
            'timezone_name': self.project.timezone_name,
            'start_at': self.start_at.isoformat(),
            'my_jobs_url': settings.FRONTEND_MY_JOBS_PAGE
        }
        return data

    def reminder_participant(self, one_day):
        if one_day:
            email_name = 'reminder_participant_tomorrow_qa_session'
        else:
            email_name = 'reminder_participant_one_hour_before_qa_session'
        headers = self.get_data_reminder()
        for team in self.project.teams.all():
            url = settings.FRONTEND_PROJECT_QUESTION_PAGE.format(
                **{
                    'project_id': self.project.pk,
                    'team_id': team.pk,
                    'section': 'swarm-session',
                    'pk': 'create',
                })
            for user in team.team_members.all():
                recipients = [user.email]
                headers.update({
                    'recipients': recipients,
                    'short_name': user.short_name,
                    'one_day': one_day,
                    'disable_notification_url': UserProfileWrapper(user).account_url,
                    'subject_args': {
                        'one_day': one_day
                    },
                    'public_url': url
                })
                handlers.mail_handler.send_mail(email_name, **headers)

    def reminder_advisor(self, one_day):
        if one_day:
            email_name = 'reminder_advisor_tomorrow_qa_session'
        else:
            email_name = 'reminder_advisor_one_hour_before_qa_session'
        headers = self.get_data_reminder()

        for advisor in self.members.all():
            user = advisor.consultant.user
            recipients = [user.email]
            headers.update({
                'recipients': recipients,
                'short_name': user.short_name,
                'one_day': one_day,
                'disable_notification_url': UserProfileWrapper(user).account_url,
                'subject_args': {
                    'one_day': one_day
                },
            })
            handlers.mail_handler.send_mail(email_name, **headers)

    def reminder_one_day_before(self):
        self.reminder_participant(True)
        self.reminder_advisor(True)

    def reminder_one_hour_before(self):
        self.reminder_participant(False)
        self.reminder_advisor(False)

    def send_advisor_selected_email(self):
        email_name = 'qa_session_advisor_selected'
        headers = self.get_data_reminder()

        for advisor in self.members.all():
            user = advisor.consultant.user
            recipients = [user.email]
            headers.update({
                'recipients': recipients,
                'short_name': user.short_name,
                'disable_notification_url': UserProfileWrapper(user).account_url,
            })
            handlers.mail_handler.send_mail(email_name, **headers)

    def send_participant_summary_email(self):
        email_name = 'qa_session_summary'
        headers = self.get_data_reminder()
        for team in self.project.teams.all():
            session_team = self.teams.filter(team=team).first()
            if not session_team:
                continue
            url = session_team.url
            for user in team.team_members.all():
                recipients = [user.email]
                headers.update({
                    'recipients': recipients,
                    'short_name': user.short_name,
                    'public_url': url,
                    'disable_notification_url': UserProfileWrapper(user).account_url,
                })
                try:
                    rating = round(session_team.rating_average, 1)
                except TypeError:
                    rating = None

                data = {
                    'total_questions': session_team.questions.count(),
                    'your_answers': session_team.total_answers_by_participant(user),
                    'rating': rating
                }
                headers.update(data)
                handlers.mail_handler.send_mail(email_name, **headers)
