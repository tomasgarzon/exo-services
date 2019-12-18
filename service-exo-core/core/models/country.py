from django.db import models
from model_utils.models import TimeStampedModel


class Country(TimeStampedModel):
    name = models.CharField(max_length=255, db_index=True)
    native_name = models.CharField(max_length=255, db_index=True)
    code_2 = models.CharField(max_length=2, db_index=True, unique=True)
    code_3 = models.CharField(max_length=3, db_index=True, unique=True)
    flag = models.CharField(max_length=255, blank=True, null=True)
