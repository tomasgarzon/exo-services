from django.conf import settings

from utils import notifications

from ..models.microlearning_average import MicroLearningAverage
from ..api.serializers.personal_quiz import PersonalQuizSerializer


def microlearning_handler(sender, user_microlearning, *args, **kwargs):
    instance = MicroLearningAverage(
        step_stream=user_microlearning.microlearning.step_stream,
        user=user_microlearning.user,
        team=user_microlearning.team)

    payload = {
        'step_pk': instance.get_step().pk,
        'object': PersonalQuizSerializer(user_microlearning).data
    }
    notifications.send_notifications(
        settings.PROJECT_TOPIC_NAME,
        'update',
        instance.__class__.__name__.lower(),
        instance.user.uuid,
        payload)
