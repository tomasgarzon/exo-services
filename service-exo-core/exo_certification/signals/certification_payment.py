from django.apps import apps


def certification_request_payment_success_handler(sender, pk, **kwargs):
    CertificationRequest = apps.get_model(
        app_label='exo_certification',
        model_name='CertificationRequest',
    )

    certification = CertificationRequest.objects.get(pk=pk)
    certification.report_pay_action()
    certification.notify_referrer(conversion=True)
