from django.db.models import When, Value


REGULAR_USER = When(
    user__consultant__isnull=True,
    then=Value(True),
)
CONSULTANT_USER = When(
    user__consultant__isnull=False,
    user__consultant__status='A',
    then=Value(True),
)
