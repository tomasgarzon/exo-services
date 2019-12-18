from django.db.models.signals import post_save
from django.apps import apps

from utils.signals import edit_slug_field
from utils.models import TagAutoSlugField

from .resource import slug_edit
from .uploaded_file import post_save_uploaded_file


def setup_signals():
    UploadedFile = apps.get_model(
        app_label='files', model_name='UploadedFile')

    edit_slug_field.connect(slug_edit, sender=TagAutoSlugField)

    post_save.connect(post_save_uploaded_file, sender=UploadedFile)
