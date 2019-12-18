from dj_anonymizer.register_models import (
    register_skip,
)

from resource import models


register_skip([
    models.Category,
    models.Resource,
    models.Tag,
])
