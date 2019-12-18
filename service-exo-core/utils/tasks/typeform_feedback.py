from celery import Task

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from typeform_feedback.tasks import TypeformWebhookMixin


class UpdateUserGenericTypeformFeedbackTask(TypeformWebhookMixin, Task):
    name = 'UpdateUserGenericTypeformFeedbackTask'
    ignore_result = True

    def get_content_type(self, response):
        form_response = self._get_form_response(response)
        hidden_fields = self._get_hidden(form_response)
        content_type_id = hidden_fields.get(
            settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_CONTENT_TYPE,
        )
        return ContentType.objects.get(pk=content_type_id)

    def get_object_id(self, response):
        form_response = self._get_form_response(response)
        hidden_fields = self._get_hidden(form_response)
        return hidden_fields.get(
            settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_OBJECT_ID,
        )

    def get_object(self, response_from_typeform):
        content_type = self.get_content_type(response_from_typeform)
        object_id = self.get_object_id(response_from_typeform)
        return content_type.get_object_for_this_type(pk=object_id)

    def run(self, *args, **kwargs):
        response_from_typeform = kwargs.get('response_from_typeform', {})
        try:
            user_feedback = self.get_object(response_from_typeform)
            user_feedback.set_typeform_response(response_from_typeform)
        except:  # noqa
            self.set_error('ContentType or object id invalid or missing')
            return None
