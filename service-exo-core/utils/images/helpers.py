# -*- coding: utf-8 -*-
"""
License boilerplate should be used here.
"""
# python 3 imports
from __future__ import absolute_import, unicode_literals

# python imports
import hashlib
import os

# django imports
from django.core.files.base import ContentFile

# 3rd. libraries imports
from pilkit.utils import save_image


def md5_checksum(content):
    """Returns the md5 checksum for the content of a given image.

    Args:
        content: a file to be used to calculate the md5 checksum.

    Returns:
        A string with the md5 checksum result of the content of the image.
    """
    md5 = hashlib.md5()
    for chunk in content.chunks():
        md5.update(chunk)
    content.seek(0)
    return md5.hexdigest()


def get_format(path):
    """Returns the file format for a given image file path.

    This function returns a file format based on the extension of the given
    image path.

    Args:
        path: a string with the file path.

    Returns:
        A string with the format of the image file.
    """
    path_name, ext = os.path.splitext(path)
    ext = ext.strip('.').lower()
    if ext == 'jpg':
        return 'jpeg'
    else:
        return ext


def save_pilimage(image, path, storage):
    """Save a pil image using django storage system.

    As a PIL image does not inherit from django file class it can not be saved
    using django storage system. So we have to load the image content to a
    django file and the save it using django storage.

    Args:
        image: a PIL image to be saved in the host.
        path: a string that indicates the file path where the image should be
            saved.
        storage: a django storage instance.

    Returns:
        A string with the path of the stored file.
    """
    content = ContentFile(b'')
    save_image(image, outfile=content, format=get_format(path))
    name = storage.save(path, content)
    content.close()
    return name
