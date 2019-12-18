from django.urls import path

from .views import (
    CreatePaymentView,
    UpdatePaymentView,
    DoRequestPaymentView,
    EmailNotifyView,
    process_webhook,
)


app_name = 'api-payments'


urlpatterns = [
    path('webhooks/', process_webhook, name='webhooks'),
    path('do-request/', DoRequestPaymentView.as_view(), name='do-request'),
    path('email_notify/<slug:hash>/', EmailNotifyView.as_view(), name='email-notify'),
    path('payment/', CreatePaymentView.as_view(), name='create-payment'),
    path('payment/<uuid>/', UpdatePaymentView.as_view(), name='update-payment'),
]
