from dj_anonymizer.register_models import (
    AnonymBase,
    register_anonym,
)
from dj_anonymizer import anonym_field
from utils.faker_factory import faker
from django.db.models.fields import Field
from consultant import models


class ConsultantAnonym(AnonymBase):
    primary_phone = anonym_field.function(faker.phone_number)
    secondary_phone = anonym_field.function(faker.phone_number)

    class Meta:
        exclude_fields = list({
            field.name for field in models.Consultant._meta.get_fields()
            if isinstance(field, Field) and field.name
            not in ['primary_phone', 'secondary_phone']
        })


class ContractingDataAnonym(AnonymBase):
    name = anonym_field.function(faker.name)
    address = anonym_field.function(faker.address)
    company_name = anonym_field.function(faker.name)

    class Meta:
        exclude_fields = list({
            field.name for field in models.ContractingData._meta.get_fields()
            if isinstance(field, Field) and field.name
            not in ['name', 'address', 'company_name']
        })


class ConsultantExOProfileAnonym(AnonymBase):
    personal_mtp = anonym_field.function(faker.text)
    availability_hours = anonym_field.function(faker.pyint)
    video_url = anonym_field.function(faker.uri)

    class Meta:
        exclude_fields = list({
            field.name for field in models.ConsultantExOProfile._meta.get_fields()
            if isinstance(field, Field) and field.name
            not in ['personal_mtp', 'availability_hours', 'video_url']
        })


register_anonym([
    (models.Consultant, ConsultantAnonym),
    (models.ContractingData, ContractingDataAnonym),
    (models.ConsultantExOProfile, ConsultantExOProfileAnonym),
])
