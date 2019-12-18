# -*- coding: utf-8 -*-
"""
License boilerplate should be used here.
"""
# python 3 imports
from __future__ import absolute_import, unicode_literals

# python imports
import logging
import os
import re
import sys
import io
import urllib

# django imports
from django.db.models.fields.files import ImageFieldFile
from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.exceptions import ImproperlyConfigured
from django.utils import six, text

# 3rd. libraries imports
from PIL import Image as PILImage
from pilkit.processors import Thumbnail, SmartCrop
from pilkit.utils import save_image

# app imports
from .helpers import get_format, md5_checksum, save_pilimage

logger = logging.getLogger(__name__)


class UniqueImageFieldFile(ImageFieldFile):
    """An ImageFieldFile that prevents duplicated uploaded files.

    This is a subclass of the file instance you get when accessing an
    Imageield from a model. This one force the name of the file to be the
    checksum of the file itself. This is done to prevent uploading the same
    file twice as we look for an existing file with the same checksum as the
    one we are trying to upload.
    """

    def save(self, name, content, save=True, default=False):
        """This save method is "almost" the same as the one from
        ImageFieldFile. The main difference is that we override the name of the
        file and check for a file with the same content as the one we are
        trying to upload.
        """
        name = self.field.generate_filename(self.instance, name)
        if default:
            checksum = text.slugify(self.instance.get_full_name())
        else:
            checksum = md5_checksum(content)
        _, ext = os.path.splitext(name)
        path, _ = os.path.split(name)
        name = '{path}{sep}{name}{ext}'.format(
            path=path,
            sep=os.path.sep,
            name=checksum,
            ext=ext,
        ).lower()

        self.name = self.storage.save(name, content)
        setattr(self.instance, self.field.name, self.name)

        # Update the filesize cache
        self._size = content.size
        self._committed = True

        # Save the object because it has changed, unless save is False
        if save:
            self.instance.save()
    save.alters_data = True


class ThumbnailsMixin(object):
    """Mixin that links an image with its thumbnails.

    This mixin can generate thumbnails base in the file instance of an
    ImageFielFile and also has methods to return the thumbnail path and url.

    To use this mixin you have to add it to a ImageFieldFile subclass and use
    that subclass as the attr_class of an ImageField. The ImageField should
    have two attributes that defines the behaviour of the thumbnails,
    `thumbnails` that enable the use of thumbnails and `thumbnail` with
    a list of integers that indicates the width in pixels of the thumbnails
    that will be created on save.
    """

    def save(self, *args, **kwargs):
        super(ThumbnailsMixin, self).save(*args, **kwargs)
        thumbnails = getattr(self.field, 'thumbnails', False)
        if thumbnails:
            self.generate_thumbnails()

    def delete(self, save=True):
        thumbnails = getattr(self.field, 'thumbnails', False)
        if thumbnails:
            self.remove_thumbnails()
        super(ThumbnailsMixin, self).delete(save=save)

    def _get_thumbnail_folder(self, width, height):
        return '_'.join((str(width), str(height)))

    def _require_thumbnail(self):
        """Raise a ValueError if field has not thumbnails enabled.
        """
        thumbnails = getattr(self.field, 'thumbnails', False)
        if not thumbnails:
            raise ValueError(
                '{} has not thumbnails enabled.'.format(self.field.name),
            )

    def get_thumbnail_url(
            self,
            width=settings.EXO_ACCOUNTS_DEFAULT_IMAGE_SIZE,
            height=settings.EXO_ACCOUNTS_DEFAULT_IMAGE_SIZE,
            generate=False):
        """Returns the url for a given size thumbnail.
        """
        self._require_thumbnail()

        url = None

        if self.url:
            self.generate_thumbnail(width, height, generate)
            url_path = self.url.split('/')
            url_path.insert(-1, self._get_thumbnail_folder(width, height))
            url = '/'.join(url_path)
        return url

    def get_thumbnail_path(self, width, height):
        """Returns the relative system path for a given size thumbnail.
        """
        self._require_thumbnail()
        if os.path.isabs(self.path):
            path = [os.path.dirname(self.path)]
        else:
            path = [self.field.upload_to]
        path.append(self._get_thumbnail_folder(width, height))
        path.append(os.path.basename(self.name))
        return os.path.join(*path)

    def generate_thumbnail(self, width, height, generate=True):
        """Generate a thumbnail for the given size.
        """
        self._require_thumbnail()
        self._require_file()
        path = self.get_thumbnail_path(width, height)
        if generate and not self.storage.exists(path):
            processor = Thumbnail(width=width, height=height, crop=False)
            try:
                fp = urllib.request.urlopen(self.url)
                img = io.BytesIO(fp.read())
            except ValueError:  # is in local
                img = self.path

            try:
                with PILImage.open(img) as image:
                    resized_image = processor.process(image)
                    save_pilimage(resized_image, path, self.storage)
            except IOError as e:
                logger.warning(e)

    def generate_thumbnails(self):
        """Generate all thumbnails for the sizes defined as default.
        """
        self._require_thumbnail()
        sizes = getattr(self.field, 'thumbnails', [])
        for width, height in sizes:
            self.generate_thumbnail(width, height)

    def remove_thumbnails(self):
        """Remove all thumbnails related with this image.

        We look for any thumbnail related with this image, those which are in a
        "digit" subfolder and with the same name as the original file.

        As we want to use django storage system, we can not remove empty
        directories.
        """
        root_path = os.path.dirname(self.path)
        try:
            thumbnail_dirs = self.storage.listdir(root_path)[0]
        except FileNotFoundError:
            return
        folders = (item for item in thumbnail_dirs
                   if re.match(r'\d+_\d+', item))
        sizes = (item.split('_') for item in folders)
        for width, height in sizes:
            path = self.get_thumbnail_path(width, height)
            self.storage.delete(path)


class StaticChoiceMixin(object):
    """Mixin that allows a _selectable image_ as fallback for an image file.

    With this mixin a ImageField can declare a _choice field_, another field of
    the ImageField's model, that stores the path to a static image file. When
    the previous ImageField has no file instance, it will return the value of
    the _choice field_.

    As with the TuhmbnailsMixin, to use this mixin you have to add it to a
    ImageFieldFile subclass and use that subclass as the attr_class of an
    ImageField. The ImageField should have an attribute that defines the field
    to be used as a fallback.
    """

    def _get_choice_field(self):
        """Returns the field of the model instance declared as fallback.
        """
        if self.field.choice_field is None:
            return None
        try:
            return getattr(self.instance, self.field.choice_field)
        except AttributeError as e:
            raise six.reraise(
                ImproperlyConfigured,
                ImproperlyConfigured(
                    '{} has no {} field.'.format(
                        self.instance,
                        self.field.choice_field,
                    ),
                    e,
                ),
                sys.exc_info()[2],
            )
    choice_field = property(_get_choice_field)

    def _get_url(self):
        if not self and self.choice_field:
            return static(self.choice_field)
        return super(StaticChoiceMixin, self).url
    url = property(_get_url)

    def _get_path(self):
        if not self and self.choice_field:
            return finders.find(self.choice_field)
        return super(StaticChoiceMixin, self).path
    path = property(_get_path)


class ThumbnailChoiceMixin(ThumbnailsMixin, StaticChoiceMixin):
    """A mixin that combines the behabiour of both ThumbnailsMixin and
    StaticChoiceMixin.

    As the choice field stores the path for a static file we must prevent the
    generation and cleared of thumbnails.
    """

    def generate_thumbnail(self, width, height, generate=True):
        if self:
            super(
                ThumbnailChoiceMixin,
                self
            ).generate_thumbnail(width, height, generate)

    def remove_thumbnails(self):
        if self:
            super(ThumbnailChoiceMixin, self).remove_thumbnails()


class CropMixin(object):
    """A mixin that crops the image to a defined "box" before saving it on
    the host.
    """

    def save(self, name, content, save=True, *args, **kwargs):
        crop_size = getattr(self.field, 'crop_size', None)
        if crop_size:
            width, height = crop_size
            processor = SmartCrop(width=width, height=height)
            with PILImage.open(content.file) as image:
                cropped_image = processor.process(image)
                path, ext = os.path.splitext(name)
                save_image(
                    cropped_image, outfile=content.file,
                    format=get_format(ext),
                )

        super(CropMixin, self).save(
            name=name,
            content=content,
            save=save,
            *args, **kwargs
        )


class NoExifMixin(object):
    """A mixin that removes all EXIF data from an image header.

    To remove the data in the header without knowing the schema of a EXIF
    header, that is a pretty confusing, we parse the file through PIL an return
    the parsed file againt to the content been saved.
    """

    def save(self, name, content, save=True, *args, **kwargs):
        with PILImage.open(content.file) as image:
            path, ext = os.path.splitext(name)
            image.save(content.file, ext=get_format(ext))
            content.file.seek(0)

        super(NoExifMixin, self).save(
            name=name,
            content=content,
            save=save,
            *args, **kwargs
        )


class CustomImageFieldFile(
    CropMixin, ThumbnailChoiceMixin,
    UniqueImageFieldFile
):
    pass
