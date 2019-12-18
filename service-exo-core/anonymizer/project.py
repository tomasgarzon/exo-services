from dj_anonymizer.register_models import (
    AnonymBase,
    register_anonym,
)
from dj_anonymizer import anonym_field
from django.db.models import Field

from utils.faker_factory import faker

from project import models


class ProjectAnonym(AnonymBase):
    name = anonym_field.function(faker.name)
    uuid = anonym_field.function(faker.uuid4)

    class Meta:
        exclude_fields = list(set(
            field.name for field in models.Project._meta.get_fields()
            if isinstance(field, Field) and field.name
            not in [
                'name',
                'uuid',
            ]
        ))


register_anonym([
    (models.Project, ProjectAnonym),
])
