from dj_anonymizer.register_models import (
    AnonymBase,
    register_anonym,
    register_skip
)
from dj_anonymizer import anonym_field

from utils.faker_factory import faker

from landing import models


class SectionAnonym(AnonymBase):
    name = anonym_field.function(faker.sentence)
    description = anonym_field.function(faker.text)
    content = anonym_field.function(faker.text)

    class Meta:
        exclude_fields = [
            'modified', 'created',
            'page', 'index']


register_anonym([
    (models.Section, SectionAnonym),
])

register_skip([
    models.Page,
])
