import logging

import requests
from django.conf import settings
from rest_framework import serializers

logger = logging.getLogger('recaptcha')


class RecaptchaSerializerMixin:

    def validate_recaptcha(self, value):
        if not settings.RECAPTCHA_ENABLED:
            return value
        try:
            r = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                {
                    'secret': settings.RECAPTCHA_PRIVATE_KEY,
                    'response': value
                },
                timeout=5
            )
            r.raise_for_status()
        except requests.RequestException as e:
            logger.exception(e)
            raise serializers.ValidationError(
                'Connection to reCaptcha server failed',
                code='connection_failed'
            )

        json_response = r.json()

        logger.debug('Recieved response from reCaptcha server: %s', json_response)
        if bool(json_response['success']):
            if settings.RECAPTCHA_SCORE_THRESHOLD > json_response['score']:
                logger.exception('Score to low: {}'.format(json_response['score']))
                raise serializers.ValidationError(
                    'Captcha score is too low, try to reload the page',
                    code='score',
                )

        else:
            if 'error-codes' in json_response:
                if 'missing-input-secret' in json_response['error-codes'] or \
                        'invalid-input-secret' in json_response['error-codes']:

                    logger.exception('Invalid reCaptcha secret key detected')
                    raise serializers.ValidationError(
                        'Connection to Captcha server failed, try again',
                        code='invalid_secret',
                    )
                else:
                    raise serializers.ValidationError(
                        'Captcha invalid or expired, try to reload the page',
                        code='expired',
                    )
            else:
                logger.exception('No error-codes received from Google reCaptcha server')
                raise serializers.ValidationError(
                    'Captcha response from Google not valid, try to reload the page',
                    code='invalid_response',
                )

        return value
