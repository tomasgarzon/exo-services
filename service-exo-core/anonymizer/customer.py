from dj_anonymizer.register_models import (
    AnonymBase,
    register_anonym,
)
from dj_anonymizer import anonym_field

from utils.faker_factory import faker

from django.db.models.fields import Field

from customer import models


class CustomerAnonym(AnonymBase):
    name = anonym_field.function(faker.name)
    created = anonym_field.function(faker.date_time)
    modified = anonym_field.function(faker.date_time)
    description = anonym_field.function(faker.text)
    phone = anonym_field.function(faker.phone_number)
    website = anonym_field.function(faker.uri)
    address = anonym_field.function(faker.address)
    postcode = anonym_field.function(faker.postcode)
    contact_person = anonym_field.function(faker.name)
    facebook = anonym_field.function(faker.uri)
    twitter = anonym_field.function(faker.uri)
    google = anonym_field.function(faker.uri)
    linkedin = anonym_field.function(faker.uri)
    blog = anonym_field.function(faker.uri)
    timezone = anonym_field.function(faker.timezone)
    market_value = anonym_field.function(faker.pyint)
    annual_revenue = anonym_field.function(faker.pyint)
    profile_picture = anonym_field.function(faker.image_url)

    class Meta:
        exclude_fields = list(set(
            field.name for field in models.Customer._meta.get_fields()
            if isinstance(field, Field) and field.name
            not in [
                'name',
                'created',
                'modified',
                'description',
                'phone',
                'website',
                'address',
                'postcode',
                'contact_person',
                'facebook',
                'twitter',
                'google',
                'linkedin',
                'blog',
                'timezone',
                'market_value',
                'annual_revenue',
                'profile_picture',
            ]
        ))


register_anonym([
    (models.Customer, CustomerAnonym),
])
