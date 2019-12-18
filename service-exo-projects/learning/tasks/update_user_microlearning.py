from celery import Task

from django.conf import settings

from typeform_feedback.tasks import TypeformWebhookMixin

from ..models import UserMicroLearning


class UpdateUserMicrolearningTask(TypeformWebhookMixin, Task):
    name = 'UpdateUserMicrolearningTask'
    ignore_result = True

    def get_object_id(self, response):
        form_response = self._get_form_response(response)
        hidden_fields = self._get_hidden(form_response)
        return hidden_fields.get(
            settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_OBJECT_ID,
        )

    def get_object(self, response_from_typeform):
        object_id = self.get_object_id(response_from_typeform)
        return UserMicroLearning.objects.get(pk=object_id)

    def get_score(self, response_from_typeform):
        form_response = self._get_form_response(response_from_typeform)
        calculate = form_response.get(
            settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_CALCULATED,
        )
        return calculate.get(
            settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_SCORE,
        )

    def run(self, *args, **kwargs):
        response_from_typeform = kwargs.get('response_from_typeform', {})
        try:
            user_microlearning = self.get_object(response_from_typeform)
            score = self.get_score(response_from_typeform)
        except Exception as e:
            self.set_error(e)
            raise e
            return None

        user_microlearning.add_typeform_response(
            score, response_from_typeform,
        )
