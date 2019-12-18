import logging

from django.apps import apps
from django.conf import settings

from celery import Task

from utils.mails.handlers import mail_handler
from utils.mails.attachments import PDFWrapper


from service.celery import app


logger = logging.getLogger('celery')


class SendPaymentReceivedEmailTask(Task):
    name = 'Send Payment Received email'
    ignore_result = False

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        msg = 'SendPaymentReceivedEmailTask.on_failure: {}-{}'.format(task_id, exc)
        logger.error(msg)
        super(SendPaymentReceivedEmailTask, self).on_failure(
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

        try:
            attachment = []
            office_wrapper = PDFWrapper(payment.attached_file)
            office_wrapper.set_filename(payment.attached_filename)
            attachment = office_wrapper.serialize()

            email_data = {
                'concept': payment.concept,
                'full_name': payment.full_name,
                'from_email': settings.EMAIL_NOTIFICATIONS_FROM,
                'recipients': [payment.email],
                'bcc': [settings.EMAIL_FINANCE],
                'attachments': attachment,
            }

            mail_handler.send_mail(
                template='payment_received',
                **email_data
            )

        except Exception as e:
            logger.error(e)
            self.retry(countdown=30, max_retries=3)


app.tasks.register(SendPaymentReceivedEmailTask())
