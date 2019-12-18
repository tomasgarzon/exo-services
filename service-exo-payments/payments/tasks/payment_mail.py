import logging

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from celery import Task

from utils.mails.handlers import mail_handler
from utils.mails.attachments import PDFWrapper


from service.celery import app


logger = logging.getLogger('celery')


class SendPaymentEmailTask(Task):
    name = 'Send Payment email'
    ignore_result = False

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        msg = 'SendPaymentEmailTask.on_failure: {}-{}'.format(task_id, exc)
        logger.error(msg)
        super(SendPaymentEmailTask, self).on_failure(
            exc,
            task_id,
            args,
            kwargs,
            einfo,
        )

    def run(self, *args, **kwargs):
        Payment = apps.get_model(
            app_label='payments',
            model_name='Payment')
        payment = Payment.objects.get(id=kwargs.get('payment_pk'))
        if payment.is_pending:
            try:
                attachment = []
                notification_url = '{}{}'.format(
                    settings.DOMAIN_NAME,
                    reverse(
                        'api:email-notify',
                        kwargs={'hash': payment._hash_code}
                    )
                )
                if payment.attached_file:
                    office_wrapper = PDFWrapper(payment.attached_file)
                    office_wrapper.set_filename(payment.attached_filename)
                    attachment = office_wrapper.serialize()

                email_data = {
                    'notify_webhook': notification_url,
                    'object_id': payment.pk,
                    'content_type_id': ContentType.objects.get_for_model(payment).pk,
                    'concept': payment.concept,
                    'detail': payment.detail,
                    'full_name': payment.full_name,
                    'amount': payment.amount_str,
                    'currency': payment.get_currency_display(),
                    'public_url': payment.url,
                    'from_email': settings.EMAIL_NOTIFICATIONS_FROM,
                    'recipients': [payment.email],
                    'attachments': attachment,
                }

                mail_handler.send_mail(
                    template='new_payment_created',
                    **email_data
                )

                payment.attached_file.delete()

            except Exception as e:
                logger.error(e)
                self.retry(countdown=30, max_retries=3)


app.tasks.register(SendPaymentEmailTask())
