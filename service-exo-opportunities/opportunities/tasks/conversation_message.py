import celery
import logging
from django.contrib.auth import get_user_model
from django.conf import settings

from auth_uuid.utils.user_wrapper import UserWrapper

from utils.mails.handlers import mail_handler
from utils.mails.config_param import enabled_config_param

from ..models import Opportunity


logger = logging.getLogger('celery-task')
MAIL_CHAT_FIRST_MESSAGE = 'chat_first_message'
CONFIG_PARAM_NAME = 'new_conversation'


class OpportunityMessageReceivedTask(celery.Task):
    name = 'OpportunityMessageReceivedTask'

    def get_data(self, opportunity, user):
        data = {}
        user_wrapper = UserWrapper(user=user)
        data['user_from_full_name'] = user_wrapper.get_full_name()
        data['user_from_title'] = user_wrapper.userTitle
        data['user_from_profile_picture'] = user_wrapper.profilePicture[1][1]
        data['title'] = '{} started a new conversation related to {}'.format(
            user_wrapper.get_full_name(),
            opportunity.title)
        return data

    def send_mail_new_message(self, user_from, user_to, opportunity, message):
        value = enabled_config_param(user_to, CONFIG_PARAM_NAME)
        if not value:
            return
        data = self.get_data(opportunity, user_from)
        user_wrapper = UserWrapper(user=user_to)
        data['recipients'] = [user_wrapper.email]
        user_is_manager = opportunity.group and user_to in opportunity.group.managers.all()
        if opportunity.created_by == user_to or user_is_manager:
            data['public_url'] = opportunity.admin_url_public
        else:
            data['public_url'] = settings.OPPORTUNITIES_CHAT_URL.format(opportunity.pk)
        data['message'] = message
        status = mail_handler.send_mail(
            template=MAIL_CHAT_FIRST_MESSAGE,
            **data)
        if not status:
            logger.error('Error sending email to {}: {}'.format(user_to, data))
            raise Exception()

    def run(self, *args, **kwargs):
        opp_pk = kwargs.get('pk')
        try:
            opportunity = Opportunity.objects.get(pk=opp_pk)
        except Opportunity.DoesnotExist:
            logger.error('Opportunity does not exist')
            raise Exception()

        try:
            created_by = get_user_model().objects.get(uuid=kwargs.get('created_by'))
        except get_user_model().DoesNotExist:
            logger.error('User created does not exist')
            raise Exception()

        try:
            other_user = get_user_model().objects.get(uuid=kwargs.get('other_user'))
        except get_user_model().DoesNotExist:
            logger.error('Other User created does not exist')
            raise Exception()

        self.send_mail_new_message(
            created_by, other_user, opportunity,
            kwargs.get('message'))
