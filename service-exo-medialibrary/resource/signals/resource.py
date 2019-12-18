from django.conf import settings
from django.apps import apps


def post_save_resource(sender, *args, **kwargs):
    if not settings.UPLOAD_REAL:
        Tag = apps.get_model(
            app_label='resource', model_name='Tag')
        tag, _ = Tag.objects.get_development_tag()
        sender.tags.add(tag)
