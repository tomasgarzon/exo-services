from typeform_feedback.models import UserGenericTypeformFeedback

from ..tasks.user_typeform_responses import NewUserTypeformResponseMailTask


def notify_by_mail_new_typeform_response(sender, uuid, response, *args, **kwargs):
    try:
        user_response = UserGenericTypeformFeedback.objects.get(uuid=uuid)
        NewUserTypeformResponseMailTask().s(
            user_response_uuid=user_response.uuid.__str__(),
            username=user_response.user.get_full_name(),
            response_related=user_response.feedback.related_to.first(),
            user_response=response,
        ).apply_async()
    except UserGenericTypeformFeedback.DoesNotExist:
        pass
