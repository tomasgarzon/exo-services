from dj_anonymizer.register_models import AnonymBase, register_anonym
from dj_anonymizer import anonym_field

from django.db.models.fields import Field
from exo_certification import models

from utils.faker_factory import faker


class CertificationRequestAnonym(AnonymBase):
    requester_email = anonym_field.function(faker.email)
    requester_name = anonym_field.function(faker.name)

    class Meta:
        exclude_fields = list(set(
            field.name for field in models.CertificationRequest._meta.get_fields()
            if isinstance(field, Field) and field.name
            not in ['requester_name', 'requester_email']
        ))


register_anonym([
    (models.CertificationRequest, CertificationRequestAnonym),
])
