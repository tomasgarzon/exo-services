import celery
import logging

from actstream.models import followers

from auth_uuid.utils.user_wrapper import UserWrapper

from utils.mails.handlers import mail_handler
from utils.notifications import send_notifications

from ..mails import Edit
from ..models import Opportunity
from ..conf import settings


logger = logging.getLogger('celery-task')


class OpportunityEditedTask(celery.Task):
    name = 'Edited opportunity'

    def get_recipients(self, opportunity):
        users_wrapper = []
        users = followers(opportunity)
        for u in users:
            users_wrapper.append(UserWrapper(user=u))
        return users_wrapper

    def send_notification(self, user, opportunity):
        data = {'opportunity': opportunity.pk}
        action = settings.OPPORTUNITIES_ACTION_EDITED_OPPORTUNITY
        send_notifications(action, user.uuid, data)

    def run(self, *args, **kwargs):
        opportunity_pk = kwargs.get('pk')
        comment = kwargs.get('comment')
        email_name = settings.OPPORTUNITIES_MAIL_VIEW_OPPORTUNITY_EDITED

        try:
            opp = Opportunity.objects.get(pk=opportunity_pk)
        except Opportunity.DoesNotExist:
            logger.error('Opportunity does not exist')
            raise Exception()
        recipients = self.get_recipients(opp)

        try:
            data = Edit(opp).get_data()
        except Exception as err:
            logger.error('Edit data exception: {}'.format(err))
            raise Exception()
        for recipient in recipients:
            user_data = data.copy()
            user_data['applicant_name'] = recipient.get_full_name()
            user_data['recipients'] = [recipient.email]
            user_data['comment'] = comment or ''
            status = mail_handler.send_mail(
                template=email_name,
                **user_data)
            if not status:
                logger.error('Error sending email to: {}'.format(user_data))
            try:
                self.send_notification(recipient.user, opp)
            except Exception as err:
                logger.error('Send notification exception: {}'.format(err))
