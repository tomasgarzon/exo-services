from dj_anonymizer.register_models import (
    AnonymBase,
    register_anonym,
)
from dj_anonymizer import anonym_field

from utils.faker_factory import faker

from django.db.models.fields import Field

from team import models


class TeamAnonym(AnonymBase):
    name = anonym_field.function(faker.name)

    class Meta:
        exclude_fields = list(set(
            field.name for field in models.Team._meta.get_fields()
            if isinstance(field, Field) and field.name
            not in [
                'name',
            ]
        ))


register_anonym([
    (models.Team, TeamAnonym),
])
