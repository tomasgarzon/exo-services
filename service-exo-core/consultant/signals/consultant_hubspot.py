import datetime

from django.conf import settings

from ..hubspot.contact import CERTIFICATION_TYPE_FOUNDATIONS

from ..tasks.hubspot_integrations import (
    HubspotContactAddCertificationTask,
    HubspotUpdateContactEmailTask,
    HubspotUpdateContactFoundationsDate,
)


def accredible_certification_created_handler(sender, user, course_name, **kwargs):
    # TODO: Add support for all Certifications levels
    if course_name == CERTIFICATION_TYPE_FOUNDATIONS:
        HubspotContactAddCertificationTask().s(
            email=user.email,
            certification_name=course_name,
        ).apply_async()


def update_user_email_at_hubspot(sender, instance, *args, **kwargs):
    update_fields = kwargs.get('update_fields', []) or []

    if 'is_primary' in update_fields and not instance.is_primary:
        old_email = instance.user.emailaddress_set.filter(
            is_primary=False,
        ).last()
        HubspotUpdateContactEmailTask().s(
            old_email=old_email.email,
            new_email=instance.email,
        ).apply_async()


def update_user_foundations_joining_date(sender, project, user, *args, **kwargs):
    """
    TODO:
    Once the relation cohort-project is done, refactor this to support all
    certification levels and notify Segment as well
    action_done = settings.INSTRUMENTATION_CERTIFICATION_ACTION_TEAM_ALLOCATION
    """
    if project.pk in settings.PROJECT_CERTIFICATION_LEVEL_1 and not settings.POPULATOR_MODE:
        date = datetime.datetime.now().replace(hour=0, minute=0, second=0)
        HubspotUpdateContactFoundationsDate().s(
            email=user.email,
            date=date,
        ).apply_async()
