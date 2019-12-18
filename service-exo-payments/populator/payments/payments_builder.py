from django.contrib.auth import get_user_model

from payments.models import Payment

from populate.populator.builder import Builder


User = get_user_model()


class PaymentBuilder(Builder):

    def create_object(self):
        payment = Payment.objects.create(
            concept=self.data.get('concept'),
            amount=self.data.get('amount'),
            currency=self.data.get('currency'),
            email=self.data.get('email'),
            full_name=self.data.get('full_name'),
            status=self.data.get('status'),
            created_by=self.data.get('created_by'),
        )

        if not payment.is_pending:
            payment.date_payment = self.data.get('date_payment')
            payment.save()
        return payment
