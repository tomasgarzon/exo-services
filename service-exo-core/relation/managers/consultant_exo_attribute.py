from django.db import models

from .level_mixin import LevelMixin


class ConsultantExOAttributeManager(LevelMixin, models.Manager):
    MAX_LEVEL_KEYWORD = 5
