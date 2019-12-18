from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from typeform_feedback.models import GenericTypeformFeedback


def post_save_step(sender, instance, created, *args, **kwargs):
    for stream, _ in settings.PROJECT_STREAM_CH_TYPE:
        instance.streams.get_or_create(
            stream=stream,
        )


def signal_create_feedback_for_each_step_stream(sender, instance, *args, **kwargs):
    if instance.step.user_has_to_fill_feedback:
        ct = ContentType.objects.get_for_model(instance)
        GenericTypeformFeedback.objects.get_or_create(
            object_id=instance.pk,
            content_type=ct,
            typeform_type=settings.TYPEFORM_FEEDBACK_CH_WEEKLY,
        )
