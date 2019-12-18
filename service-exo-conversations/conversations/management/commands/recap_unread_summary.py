import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model

from auth_uuid.utils.user_wrapper import UserWrapper

from utils.mails.handlers import mail_handler
from utils.mails.config_param import enabled_config_param
from utils.related_info import get_info_related

from ...models import Conversation, Message


logger = logging.getLogger('service')
EMAIL_NAME = 'chat_summary_unread'
DAILY = 'D'
WEEKLY = 'W'
CONFIG_PARAM_NAME = {
    DAILY: 'daily_recap_unread',
    WEEKLY: 'weekly_recap_unread'
}
CONVERSATION_TITLE = {
    settings.CONVERSATIONS_CH_OPPORTUNITIES: 'messages related to opportunity {}',
    settings.CONVERSATIONS_CH_PROJECT: 'messages related to the project {}',
    settings.CONVERSATIONS_CH_USER: 'messages from {}',
    settings.CONVERSATIONS_CH_EXO_PROJECT: 'messages related to the project {}',
}


class Command(BaseCommand):
    help = ('Conversations recap summary')

    def add_arguments(self, parser):
        parser.add_argument(
            '-p', '--period', nargs='+', type=str,
            help='Period of time report'
        )

    def get_conversations_with_messages(self, start_date, end_date):
        return Conversation.objects.filter(
            messages__created__date__gte=start_date,
            messages__created__date__lte=end_date
        ).annotate(total=Count('messages'))

    def generate_conversation_for_users(self, conversations):
        users = {}
        for c in conversations:
            for conv_user in c.users.all():
                user = conv_user.user
                unread_messages = Message.objects.filter(
                    conversation=c).exclude(users__user=user)
                if not unread_messages.exists():
                    continue
                if user.uuid.__str__() not in users:
                    users[user.uuid.__str__()] = []
                users[user.uuid.__str__()].append([c, unread_messages])
        return users

    def send_email(self, user, conversations, period):
        user_wrapper = UserWrapper(user=user)
        data = {}
        if period == DAILY:
            data['subject_args'] = {'period': 'Daily'}
        else:
            data['subject_args'] = {'period': 'Weekly'}
        data['total'] = sum(map(lambda x: x[1].count(), conversations))
        data['name'] = user_wrapper.get_full_name()
        data['conversations'] = []
        for conversation, messages in conversations:
            url, related_title = get_info_related(conversation, user)
            data_conversation = {}
            data_conversation['total'] = messages.count()
            data_conversation['message'] = messages.first().message
            data_conversation['url'] = url
            title = CONVERSATION_TITLE.get(conversation._type).format(related_title)
            data_conversation['title'] = title
            data['conversations'].append(data_conversation)
        data['recipients'] = [user_wrapper.email]
        status = mail_handler.send_mail(
            template=EMAIL_NAME,
            **data)
        if not status:
            logger.error('Error sending email to: {}'.format(data))
            raise Exception('Error sending email to: {}'.format(data))

    def handle(self, *args, **options):
        self.stdout.write('Send recap summary:')
        period = options.get('period')[0]
        if period == DAILY:
            start_date = timezone.now().date()
            end_date = timezone.now().date()
        else:
            start_date = (timezone.now() - timedelta(days=6)).date()
            end_date = timezone.now().date()
        conversations = self.get_conversations_with_messages(
            start_date, end_date)
        users = self.generate_conversation_for_users(conversations)
        for user_uuid, conversations in users.items():
            user = get_user_model().objects.get(uuid=user_uuid)
            value = enabled_config_param(user, CONFIG_PARAM_NAME[period])
            if not value:
                continue
            self.send_email(user, conversations, period)

        self.stdout.write('Total users: {}'.format(len(users.keys())))
        self.stdout.write('Finish!!')
