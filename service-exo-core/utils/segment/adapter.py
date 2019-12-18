from abc import ABC

from django.conf import settings

from .tasks import SegmentIdentifyTask, SegmentEventTask


class SegmentAnalytics(ABC):

    @classmethod
    def identify(cls, user):
        if not settings.POPULATOR_MODE and not settings.TEST_MODE:
            SegmentIdentifyTask().s(
                uuid=str(user.uuid),
                email=user.email,
                name=user.full_name,
            ).apply_async()

    @classmethod
    def event(cls, user, category, event, **kwargs):
        kwargs['category'] = category
        kwargs['event'] = event
        if not settings.POPULATOR_MODE and not settings.TEST_MODE:
            SegmentEventTask().s(
                uuid=str(user.uuid),
                event='{} - {}'.format(category, event),
                payload=kwargs,
            ).apply_async()
