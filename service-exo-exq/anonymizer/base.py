from __future__ import absolute_import

from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session

from dj_anonymizer.register_models import (
    register_skip
)


User = get_user_model()


register_skip([
    User,
    ContentType,
    Group,
    Permission,
    LogEntry,
    Session,
])
