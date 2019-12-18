from dj_anonymizer.register_models import (
    AnonymBase,
    register_anonym,
)

from jobs import models


class JobAnonym(AnonymBase):

    class Meta:
        exclude_fields = [
            'uuid',
            'related_uuid',
            'related_class',
            'status',
            'status_detail',
            'badge',
            'title',
            'start',
            'end',
            'url',
            'created',
            'modified',
            'extra_data'
        ]


register_anonym([
    (models.Job, JobAnonym),
])
