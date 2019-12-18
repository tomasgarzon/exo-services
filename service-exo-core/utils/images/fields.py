# -*- coding: utf-8 -*-
"""
License boilerplate should be used here.
"""
# python 3 imports
from __future__ import absolute_import, unicode_literals

# python imports
import logging
import random

# django imports
from django.db import models
from django.db.models import signals
from django.core.files.base import ContentFile

# app imports
from .files import CustomImageFieldFile
from .profile import create_image_profile

logger = logging.getLogger(__name__)


class PowerImageField(models.ImageField):
    """An ImageField that has a selectable fallback image, thumbnails and crop.

    This field works the same way as ImageField but accepts additional
    arguments, crop_size, choice_file and thumbnail_size. The first one is an
    optional declaration of a tuple of width/height with the final size that
    the image file should have. Choice_field is a literal with the name of a
    field that store a relative static path for a image that is used when the
    ImageField has no image itself. The last one, thumbnail_size, declares the
    thumbnail sizes to be created.
    """
    attr_class = CustomImageFieldFile

    def __init__(
        self, crop_size=None, choice_field=None,
        thumbnails=None, backgrounds=None, **kwargs
    ):
        super(PowerImageField, self).__init__(**kwargs)
        self.crop_size = crop_size
        self.choice_field = choice_field
        self.thumbnails = thumbnails
        self.backgrounds = backgrounds

    def deconstruct(self):
        name, path, args, kwargs = (
            super(PowerImageField, self).deconstruct()
        )

        if self.thumbnails:
            kwargs['thumbnails'] = self.thumbnails

        if self.choice_field:
            kwargs['choice_field'] = self.choice_field

        if self.backgrounds:
            kwargs['backgrounds'] = self.backgrounds

        return name, path, args, kwargs

    def contribute_to_class(self, cls, name):
        super(PowerImageField, self).contribute_to_class(cls, name)
        if not cls._meta.abstract:
            signals.pre_save.connect(
                self.remove_unused_files,
                sender=cls,
            )
            signals.pre_save.connect(
                self.create_profile_default,
                sender=cls,
            )

    def remove_unused_files(self, instance, *args, **kwargs):
        try:
            old_instance = instance._meta.default_manager.get(pk=instance.pk)
        except instance.DoesNotExist:
            old_instance = None

        if old_instance:
            db_image = getattr(old_instance, self.name)
            current_image = getattr(instance, self.name)
            if db_image and db_image != current_image:
                db_image.delete(save=False)

    def create_profile_default(self, instance, *args, **kwargs):
        field = getattr(instance, self.name)
        if not field.name and self.backgrounds:
            if self.backgrounds[0] == 'username':
                background = None
            else:
                background = random.choice(self.backgrounds)
            content = create_image_profile(
                instance.get_letter_initial(),
                color=background,
            )
            content_file = ContentFile(content)
            field.save(
                '%s.png' % (instance.get_letter_initial()),
                content_file, False,
                default=True,
            )
