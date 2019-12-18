from django.conf import settings

from actstream.models import followers

from utils.mail import handlers
from utils.mail.mails_mixin import EmailMixin
from utils.dates import increase_date
from consultant.models import Consultant
from custom_auth.helpers import UserProfileWrapper

from .topic_hub import (
    PostCircleCreated,
    PostAnnouncementCreated,
    PostAnnouncementReplied)
from .ask_ecosystem import AskToEcosystemCreated, AskToEcosystemReplied


class PostEmailMixin(EmailMixin):

    def get_email_delay(self):
        return increase_date(seconds=settings.FORUM_NEW_POST_DELAY)

    def new_topic_created(self):
        email_name = 'post_circle_created'
        for user in followers(self.content_object):
            if user == self.created_by:
                continue
            recipients = [user.email]
            headers_json = PostCircleCreated(self).get_data()
            headers = {
                'recipients': recipients,
                'disable_notification_url': UserProfileWrapper(user).account_url
            }
            headers.update(headers_json)
            handlers.mail_handler.send_mail(email_name, **headers)

    def new_announcement_created(self):
        email_name = 'post_announcement_created'
        for consultant in Consultant.objects.all():
            user = consultant.user
            recipients = [user.email]
            headers_json = PostAnnouncementCreated(self).get_data()
            headers = {
                'recipients': recipients,
                'disable_notification_url': UserProfileWrapper(user).account_url,
            }
            headers.update(headers_json)
            handlers.mail_handler.send_mail(email_name, **headers)

    def new_question_created(self):
        email_name = 'ask_to_ecosystem_created'
        consultants = Consultant.objects.filter_consulting_enabled()
        for consultant in consultants:
            user = consultant.user
            if user == self.created_by:
                continue
            recipients = [user.email]
            headers_json = AskToEcosystemCreated(self).get_data()
            headers = {
                'recipients': recipients,
                'disable_notification_url': UserProfileWrapper(user).account_url,
            }
            headers.update(headers_json)
            handlers.mail_handler.send_mail(email_name, **headers)

    def new_question_reply(self, answer):
        email_name = 'ask_to_ecosystem_replied'
        user = self.created_by
        recipients = [user.email]
        headers_json = AskToEcosystemReplied(answer.post, answer).get_data()
        headers = {
            'recipients': recipients,
            'disable_notification_url': UserProfileWrapper(user).account_url,
        }
        headers.update(headers_json)
        handlers.mail_handler.send_mail(email_name, **headers)

    def new_announcement_reply(self, answer):
        email_name = 'post_announcement_replied'
        user = self.created_by
        recipients = [user.email]
        recipients_cc = list(self.get_group_destinataries(
            settings.MAIL_SUPPORT_LIST_MAIL_GROUP,
        ))
        headers_json = PostAnnouncementReplied(answer.post, answer).get_data()
        headers = {
            'recipients': recipients,
            'short_name': user.short_name,
            'cc': recipients_cc,
            'disable_notification_url': UserProfileWrapper(user).account_url,
        }
        headers.update(headers_json)
        handlers.mail_handler.send_mail(email_name, **headers)

    def send_new_post_mention(self, user_mentioned):
        from ...tasks import PostMentionSendEmailTask
        kwargs = {
            'eta': increase_date(seconds=settings.FORUM_NEW_POST_DELAY)
        }
        PostMentionSendEmailTask().s(
            user_metioned_pk=user_mentioned.pk,
            post_pk=self.pk,
        ).apply_async(**kwargs)

    def send_new_answer_mention(self, answer, user_mentioned):
        from ...tasks import AnswerMentionSendEmailTask
        kwargs = {
            'eta': increase_date(seconds=settings.FORUM_NEW_POST_DELAY)
        }
        AnswerMentionSendEmailTask().s(
            user_metioned_pk=user_mentioned.pk,
            post_pk=self.pk,
            answer_pk=answer.pk,
        ).apply_async(**kwargs)

    def send_email_reply(self, answer):
        from ...tasks import PostSendEmailReplyTask

        kwargs = {}

        if answer.created_by == answer.post.created_by:
            return None

        if self.is_project:
            kwargs['eta'] = self.get_email_delay()

        PostSendEmailReplyTask().s(
            post_pk=self.pk,
            answer_pk=answer.pk,
        ).apply_async(**kwargs)

    def send_email_created(self):
        from ...tasks import PostSendEmailCreatedTask

        kwargs = {}

        if self.is_circle or self.is_announcement or self.is_project:
            kwargs['eta'] = self.get_email_delay()

        PostSendEmailCreatedTask().s(
            post_pk=self.pk
        ).apply_async(**kwargs)
