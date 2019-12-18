from dj_anonymizer.register_models import (
    AnonymBase,
    register_anonym,
)
from dj_anonymizer import anonym_field
from django.db.models import Field

from utils.faker_factory import faker

from exo_accounts import models


class SocialNetworkAnonym(AnonymBase):
    created = anonym_field.function(faker.date_time)
    modified = anonym_field.function(faker.date_time)
    value = anonym_field.function(faker.uri)

    class Meta:
        exclude_fields = list(set(
            field.name for field in models.SocialNetwork._meta.get_fields()
            if isinstance(field, Field) and field.name
            not in [
                'primary_phone',
                'secondary_phone',
            ]
        ))


register_anonym([
    (models.SocialNetwork, SocialNetworkAnonym),
])
