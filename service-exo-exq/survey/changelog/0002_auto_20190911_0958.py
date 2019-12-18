# -*- coding: utf-8 -*-
# Generated for Django 2.2.5 on 2019-09-11 09:58
from __future__ import unicode_literals
from django.conf import settings

from exo_changelog import change, operations

from ..models import Option, Answer


def fix_business_model_option():
    changes = [
        (0.75, 0.94),
        (0.9, 0.96)
    ]

    for previous, new in changes:
        Option.objects.filter(
            question__section=settings.SURVEY_CH_BUSINESS_MODEL,
            score=previous).update(score=new)
        Answer.objects.filter(
            question__section=settings.SURVEY_CH_BUSINESS_MODEL,
            score=previous).update(score=new)


class Change(change.Change):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        operations.RunPython(fix_business_model_option),
    ]
