from django.urls import path

from .views import DoPayment, InvoicePDF

app_name = 'payments'


urlpatterns = [
    path('do-payment/<slug:slug>/', DoPayment.as_view(), name='do_payment'),
    path('dopayment/<slug:slug>/', DoPayment.as_view()),
    path('invoice/<int:pk>/', InvoicePDF.as_view(), name='download-pdf'),
]
