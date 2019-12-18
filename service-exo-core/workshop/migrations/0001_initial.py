# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-01-04 13:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import workshop.managers.workshop


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkShop',
            fields=[
                (
                    'project_ptr', models.OneToOneField(
                        auto_created=True, on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True, primary_key=True, serialize=False, to='project.Project',
                    ),
                ),
            ],
            options={
                'verbose_name_plural': 'WorkShops',
                'verbose_name': 'WorkShop',
            },
            bases=('project.project',),
            managers=[
                ('objects', workshop.managers.workshop.WorkshopManager()),
            ],
        ),
    ]