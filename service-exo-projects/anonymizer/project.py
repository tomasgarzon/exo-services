from dj_anonymizer.register_models import (
    AnonymBase,
    register_anonym,
)
from dj_anonymizer import anonym_field

from utils.faker_factory import faker

from project import models
from team import models as team_models


class ProjectAnonym(AnonymBase):
    name = anonym_field.function(faker.sentence)
    customer = anonym_field.function(faker.sentence)
    description = anonym_field.function(faker.text)

    class Meta:
        exclude_fields = [
            'uuid',
            'status',
            'start',
            'end',
            'content_template',
            'template_name',
            'accomplish',
            'transform',
            'playground',
            'comment',
            'category',
            'location',
            'place_id',
            'created',
            'modified',
            'created_by',
            'permissions',
        ]


class TeamAnonym(AnonymBase):
    name = anonym_field.function(faker.sentence)

    class Meta:
        exclude_fields = [
            'uuid',
            'project',
            'stream',
            'created',
            'modified',
            'image',
            'created_by',
            'permissions',
            'action_object_actions',
            'actor_actions',
            'target_actions'
        ]


register_anonym([
    (models.Project, ProjectAnonym),
    (team_models.Team, TeamAnonym),
])
