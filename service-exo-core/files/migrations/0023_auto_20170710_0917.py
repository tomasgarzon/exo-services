# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-10 09:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0022_resource_file_size'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='_Tagulous_Resource_tags',
            new_name='Tagulous_Resource_tags',
        ),
    ]