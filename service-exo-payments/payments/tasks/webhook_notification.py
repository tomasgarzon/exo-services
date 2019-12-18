import requests
import logging

from django.apps import apps
from django.conf import settings

from service.celery import app

from celery import Task


logger = logging.getLogger('celery')


class SendWebhookTask(Task):
    name = 'Send Webhook Payment Notification'
    ignore_result = False

    def get_api_status(self, status):
        statuses_map = {
            settings.PAYMENTS_CH_CANCELED: 'C',
            settings.PAYMENTS_CH_ERASED: 'C',
            settings.PAYMENTS_CH_PAID: 'A',
        }

        return statuses_map.get(status, 'P')

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        msg = 'SendWebhookTask.on_failure: {}-{}'.format(task_id, exc)
        logger.error(msg)
        super(SendWebhookTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def run(self, *args, **kwargs):
        pk = kwargs.get('pk')

        Payment = apps.get_model(
            app_label='payments',
            model_name='Payment')
        payment = Payment.objects.get(pk=pk)

        try:
            logger.info('SendWebhookTask.run: {}'.format(pk))
            payment_method = payment.get_alternative_payment_mode_display()
            if not payment_method:
                payment_method = settings.PAYMENTS_METHDO_CARD
            data = {
                'token': payment.token,
                'payment_id': pk,
                'payment_status': self.get_api_status(payment.status),
                'payment_method': payment_method,
            }
            auth_header = {'USERNAME': settings.AUTH_SECRET_KEY}
            response = requests.put(payment.url_notification, json=data, headers=auth_header)
            assert response.ok
            logger.info('SendWebhookTask.run: {}'.format(response.content))
        except AssertionError:
            logger.error('SendWebhookTask.run: Request not valid: {}'.format(response.content))
            raise Exception('Response error')
        except requests.Timeout as err:
            message = 'SendWebhookTask.run: requests.Timeout: {}-{}'.format(err, payment.url_notification)
            logger.error(message)
            self.retry(countdown=60, max_retries=3)
        except requests.RequestException as err:
            message = 'SendWebhookTask.run: requests.RequestException: {}-{}'.format(err, payment.url_notification)
            logger.error(message)
            self.retry(countdown=60, max_retries=3)
        except Exception as err:
            message = 'SendWebhookTask.run: requests.Exception: {}'.format(err)
            logger.error(message)
            self.retry(countdown=60, max_retries=3)


app.tasks.register(SendWebhookTask())
