from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from typeform_feedback.models import GenericTypeformFeedback

from ..models import Step
from ..tasks import ProjectStartChangedTask


def post_save_step(sender, instance, created, *args, **kwargs):
    for stream in instance.project.streams.all():
        instance.streams.get_or_create(stream=stream)

    if instance == instance.project.steps.last() and instance.end is not None:
        project = instance.project
        project.end = instance.end
        project.save()


def step_started_changed_handler(sender, instance, *args, **kwargs):
    Step.objects.modify_steps(
        instance.project,
        instance)
    if not instance.project.is_draft:
        ProjectStartChangedTask().s(step_id=instance.id).apply_async()


def create_feedback_for_each_step_stream_handler(sender, instance, *args, **kwargs):
    if instance.step.user_has_to_fill_feedback:
        ct = ContentType.objects.get_for_model(instance)
        GenericTypeformFeedback.objects.get_or_create(
            object_id=instance.pk,
            content_type=ct,
            typeform_type=settings.TYPEFORM_FEEDBACK_CH_WEEKLY,
        )
