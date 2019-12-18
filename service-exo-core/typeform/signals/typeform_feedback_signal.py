from django.conf import settings

from utils import notifications


def post_save_typeform_feedback_handler(sender, instance, created, *args, **kwargs):
    action = 'create' if created else 'update'
    related_to_object = instance.feedback.related_to.first()
    if hasattr(related_to_object, 'project'):
        project = related_to_object.project
        user_projects = project.get_granted_users(
            [settings.PROJECT_PERMS_VIEW_PROJECT])
        for user in user_projects:
            data = {
                'status': instance.status,
                'user_id': instance.user.id,
                'typeform_url': instance.url,
            }
            notifications.send_notifications(
                settings.PROJECT_TOPIC_NAME,
                action,
                instance.__class__.__name__.lower(),
                user.uuid,
                data)
