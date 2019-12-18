from __future__ import absolute_import

import stripe

from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.http.response import Http404
from django.views.generic.detail import SingleObjectMixin

from wkhtmltopdf.views import PDFTemplateView

from .models import Payment


class DoPayment(DetailView):

    model = Payment
    slug_field = '_hash_code'

    def get_queryset(self):
        return self.model.objects.filter(
            status__in=settings.PAYMENTS_VALID_STATUS_UPDATE)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return context

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            context = self.get_context_data(object=self.object)

            if not settings.POPULATOR_MODE:
                # Generates stripe session
                stripe.api_key = settings.STRIPE_SECRET_KEY
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    customer_email=self.object.email,
                    line_items=[{
                        'name': self.object.concept,
                        'amount': int(self.object.amount_total * 100),
                        'currency': 'eur',
                        'quantity': 1,
                    }],
                    success_url=settings.PAYMENTS_REDIRECT_AFTER_PAYMENT_SUCCESS,
                    cancel_url=settings.PAYMENTS_REDIRECT_AFTER_PAYMENT_CANCEL,
                )
                self.object.intent_id = session.payment_intent
                self.object.save(update_fields=['intent_id'])
                context['stripe_session'] = session.id

            response = self.render_to_response(context)
        except Http404:
            response = redirect('/404')

        return response


class InvoicePDF(
        SingleObjectMixin, PDFTemplateView):
    template_name = 'invoices/invoice.html'
    model = Payment
    context_object_name = 'payment'
    raise_exception = True

    @property
    def filename(self):
        return 'invoice_{}.pdf'.format(self.object._hash_code)

    def get_context_data(self, *args, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(*args, **kwargs)
        return context
