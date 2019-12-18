from django.conf import settings


def frontend(request):
    return {
        'service_exo_mail_host': settings.SERVICE_EXO_MAIL_HOST,
        'service_exo_payment_host': settings.SERVICE_EXO_PAYMENT_HOST,
    }
