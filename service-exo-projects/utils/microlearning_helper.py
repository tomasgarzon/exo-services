from django.conf import settings

from project.models import StepStream
from populator.projects.step_helper import TYPEFORM_URL


def fix_weekly_quiz(project):
    for step in project.steps.all():
        if step.index in TYPEFORM_URL:
            core_url, edge_url = TYPEFORM_URL.get(step.index)
            update_microlearning_url(
                step=step,
                stream=settings.UTILS_STREAM_CH_CORE,
                url=core_url)
            update_microlearning_url(
                step=step,
                stream=settings.UTILS_STREAM_CH_EDGE,
                url=edge_url)


def update_microlearning_url(step, stream, url):
    try:
        step_stream = step.streams.get(stream__code=stream)
    except StepStream.DoesNotExist:
        return
    microlearning = step_stream.microlearning
    microlearning.typeform_url = url
    microlearning.save(update_fields=['typeform_url'])
