# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-26 08:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0002_auto_20160426_0812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='read_perms',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='node',
            name='write_perms',
            field=models.CharField(max_length=50),
        ),
    ]