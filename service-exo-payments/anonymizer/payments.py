from dj_anonymizer.register_models import (
    AnonymBase,
    register_anonym,
)
from dj_anonymizer import anonym_field

from utils.faker_factory import faker

from payments import models


class PaymentAnonym(AnonymBase):
    email = anonym_field.function(faker.email)
    concept = anonym_field.function(faker.text)
    full_name = anonym_field.function(faker.name)
    company_name = anonym_field.function(faker.name)
    notes = anonym_field.function(faker.text)
    tax_id = anonym_field.function(faker.text)
    address = anonym_field.function(faker.address)

    class Meta:
        exclude_fields = [
            'created',
            'modified',
            'created_by',
            '_hash_code',
            '_stripe_auth_token_code',
            '_stripe_payment_id',
            'amount',
            'currency',
            'status',
            'date_payment',
            'url_notification',
            'email_status',
            'alternative_payment_mode',
            'intent_client_secret_id',
            'email_url',
            'detail',
            'invoice_id',
            'intent_id',
            'alternative_payment_comment',
            'attached_file',
            '_type',
            'send_invoice',
            'send_by_email',
            'rate',
            'vat',
            'uuid',
            'country',
            'country_code',
        ]


register_anonym([
    (models.Payment, PaymentAnonym),
])
