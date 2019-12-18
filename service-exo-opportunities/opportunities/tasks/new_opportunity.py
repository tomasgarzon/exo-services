import celery

import logging

from django.contrib.auth import get_user_model
from django.utils import timezone

from utils.mails.handlers import mail_handler
from utils.notifications import send_notifications

from ..mails import Create, CreateWithoutAgreementSigned
from ..models import Opportunity
from ..conf import settings
from ..api.serializers.opportunity_list import OpportunityListSerializer
from ..recipients_helper import _get_recipients

logger = logging.getLogger('celery-task')
Request = type('Request', (object,), {'user': None, 'view': {'action': ''}, 'GET': {}})


class NewOpportunityTask(celery.Task):
    name = 'New opportunity'

    def _send_notification(self, user, opportunity):
        request = Request()
        request.user = user
        serializer = OpportunityListSerializer(
            opportunity,
            context={'request': request})
        data = serializer.data
        action = settings.OPPORTUNITIES_ACTION_NEW_OPPORTUNITY

        send_notifications(action, user.uuid, data)

    def _notify_by_email(self, recipient, opp):

        if recipient.get('has_signed_marketplace_agreement', True):
            user_data = Create(opp).get_data()
            email_name = settings.OPPORTUNITIES_MAIL_VIEW_NEW_OPPORTUNITY
        else:
            user_data = CreateWithoutAgreementSigned(opp, recipient).get_data()
            email_name = settings.OPPORTUNITIES_MAIL_VIEW_NEW_OPPORTUNITY_WITHOUT_AGREEMENT

        status = mail_handler.send_mail(
            template=email_name,
            recipients=[recipient.get('email')],
            **user_data)

        if not status:
            logger.error('NewOpportunityTask - Error sending email to: {}'.format(recipient.get('email')))

    def _notify_realtime(self, recipient, opp):
        user, _ = get_user_model().objects.get_or_create(uuid=recipient.get('uuid'))
        self._send_notification(user, opp)

    def clear_recipients(self, recipients, opp, user=None):
        if user is None:
            user_uuids = opp.users_tagged.values_list('user__uuid', flat=True)
        else:
            user_uuids = [user.uuid]
        return [x for x in recipients if x.get('uuid').__str__() in user_uuids.__str__()]

    def run(self, *args, **kwargs):
        logger.info('NewOpportunityTask: Calling to can-receive-opportunities: {}'.format(kwargs.get('pk')))

        opportunity_pk = kwargs.get('pk')
        user_pk = kwargs.get('user_pk')
        user = None
        if user_pk:
            user = get_user_model().objects.get(pk=user_pk)
        recipients = _get_recipients()

        try:
            opp = Opportunity.objects.get(pk=opportunity_pk)
            if opp.is_opened and not settings.OPPORTUNITIES_SEND_WHEN_CREATED:
                return
            if opp.is_tagged:
                recipients = self.clear_recipients(recipients, opp, user)
            for recipient in recipients:
                if recipient.get('uuid').__str__() == opp.created_by.uuid.__str__():
                    continue
                self._notify_by_email(recipient, opp)
                self._notify_realtime(recipient, opp)
            opp.sent_at = timezone.now()
            opp.save()
        except Opportunity.DoesNotExist:
            logger.error('NewOpportunityTask - Opportunity does not exist: {}'.format(opportunity_pk))
            raise Exception()
        except Exception as err:
            logger.error('NewOpportunityTask - Exception {}-{}'.format(err, opportunity_pk))
            raise Exception()
