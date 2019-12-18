# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-04-09 17:38
from __future__ import unicode_literals
import shutil
import os
import subprocess

from django.conf import settings

from exo_changelog import change, operations    # noqa


OLD_SIZES = ((32, 32), (56, 56), (150, 150))


def delete_old_thumnails():

    if settings.DEFAULT_FILE_STORAGE == 'django.core.files.storage.FileSystemStorage':
        base_dir = os.path.dirname(os.path.dirname(__file__))
        exolever_root_dir = '/'.join(base_dir.split('/')[:-1])
        avatars_dir = '{}/{}'.format(exolever_root_dir, 'media/avatars/')
        for size in OLD_SIZES:
            try:
                shutil.rmtree('{}{}'.format(avatars_dir, '{}_{}'.format(size[0], size[1])))
            except FileNotFoundError:  # noqa
                pass
    elif settings.DEFAULT_FILE_STORAGE == 'utils.storages.media_storage.MediaStorage':
        media_bucket_url = 's3://{}/{}/avatars/'.format(
            settings.AWS_STORAGE_BUCKET_NAME,
            settings.MEDIAFILES_LOCATION
        )

        for size in OLD_SIZES:
            subprocess.run([
                's3cmd',
                'del',
                '--recursive',
                '{}{}'.format(media_bucket_url, '{}_{}'.format(size[0], size[1]))
            ])


class Change(change.Change):

    dependencies = [
        ('exo_accounts', '0001_initial'),
    ]

    operations = []     # noqa
