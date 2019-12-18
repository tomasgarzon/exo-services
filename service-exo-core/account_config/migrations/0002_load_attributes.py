# -*- coding: utf-8 -*-
"""
License boilerplate should be used here.
"""
# python 3 imports
from __future__ import absolute_import, unicode_literals

# django imports
from django.core.management import call_command
from django.db import migrations


def load_initial_data(apps, schema_editor):
    call_command('update_or_create_config_params')


class Migration(migrations.Migration):

    dependencies = [
        ('account_config', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_initial_data)
    ]
