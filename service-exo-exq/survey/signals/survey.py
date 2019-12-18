from django.conf import settings

from guardian.shortcuts import assign_perm

from ..tasks import SurveyFilledTask


def post_save_survey_handler(sender, instance, created, *args, **kwargs):
    if created:
        assign_perm(
            settings.SURVEY_PERMS_VIEW,
            instance.created_by, instance)


def post_survey_filled_handler(sender, instance, *args, **kwargs):
    if not settings.POPULATOR_MODE:
        SurveyFilledTask().s(
            pk=instance.pk).apply_async()
