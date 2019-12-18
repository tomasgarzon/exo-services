# -*- coding: utf-8 -*-
"""
License boilerplate should be used here.
"""

# python 3 imports
from __future__ import absolute_import, unicode_literals

# python imports
import logging

# 3rd. libraries imports
from appconf import AppConf

# django imports
from django.conf import settings  # noqa

logger = logging.getLogger(__name__)


class FileConfig(AppConf):

    TEXT_HTML = 'text/html'
    TEXT_PLAIN = 'text/plain'
    APPLICATION_RTF = 'application/rtf'
    APPLICATION_VND_OASIS = 'application/vnd.oasis.opendocument.text'
    APPLICATION_PDF = 'application/pdf'
    APPLICATION_VND_XML_DOC = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    APPLICATION_VND_XML_SHEET = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    APPLICATION_VND_XML_SPREADSHEET = 'application/x-vnd.oasis.opendocument.spreadsheet'
    TEXT_CSV = 'text/csv'
    IMG_JPEG = 'image/jpeg'
    IMG_PNG = 'image/png'
    IMG_SVG = 'image/svg+xml'
    APPLICATION_VND_PRESENTATION = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    APPLICATION_VND_GOOGLE = 'application/vnd.google-apps.script+json'
    AUDIO_MPEG = 'audio/mpeg'
    AUDIO_MP3 = 'audio/mp3'
    APPLICATION_ZIP = 'application/zip'
    APPLICATION_X_ZIP = 'application/x-zip-compressed'
    APPLICATION_OCTET = 'application/octet-stream'
    DEFAULT = 'default'

    MIMETYPE = {
        TEXT_HTML: 'file-text-o',
        TEXT_PLAIN: 'file-text-o',
        APPLICATION_RTF: 'file-text-o',
        APPLICATION_VND_OASIS: 'file-word-o',
        APPLICATION_PDF: 'file-pdf-o',
        APPLICATION_VND_XML_DOC: 'file-word-o',
        APPLICATION_VND_XML_SHEET: 'file-excel-o',
        APPLICATION_VND_XML_SPREADSHEET: 'file-excel-o',
        TEXT_CSV: 'file-text-o',
        IMG_JPEG: 'file-image-o',
        IMG_PNG: 'file-image-o',
        IMG_SVG: 'file-image-o',
        APPLICATION_VND_PRESENTATION: 'file-powerpoint-o',
        APPLICATION_VND_GOOGLE: 'file-o',
        AUDIO_MPEG: 'music',
        AUDIO_MP3: 'music',
        APPLICATION_ZIP: 'file-zip-o',
        APPLICATION_X_ZIP: 'file-zip-o',
        APPLICATION_OCTET: 'file-zip-o',
        DEFAULT: 'file-o',
    }
    TYPE_LINK = 'link'

    RESOURCE_STORAGE = 'files.storage.file_system.ResourceStorage'

    GENERAL_TAG = 'general'
    USER_TAG = 'user'
    HIDE_TAG = 'hide'
    S3_RESOURCE_FOLDER = 'resources'

    UPLOADED_FILE_PERM_FULL = 'full_view'
    UPLOADED_FILE_PERM_VIEW = 'view'

    CDN_FILESTACK = 'cdn.filestackcontent.com'

    UPLOADED_FILE_STATUS_ACTIVE = 'Stored'
    UPLOADED_FILE_STATUS_INTRANSIT = 'InTransit'
    UPLOADED_FILE_STATUS_FAILED = 'Failed'
    UPLOADED_FILE_STATUS_DISABLED = 'Disabled'

    UPLOADED_FILE_STATUS_CH = (
        (UPLOADED_FILE_STATUS_ACTIVE, 'Active'),
        (UPLOADED_FILE_STATUS_INTRANSIT, 'InTransit'),
        (UPLOADED_FILE_STATUS_FAILED, 'Failed'),
        (UPLOADED_FILE_STATUS_DISABLED, 'Disabled'),
    )

    VISIBILITY_PRIVATE = 'P'
    VISIBILITY_GROUP = 'G'

    VISIBILITY_CHOICES = (
        (VISIBILITY_PRIVATE, 'Private'),
        (VISIBILITY_GROUP, 'Public with group'),
    )
