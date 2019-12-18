# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-02-01 11:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import zoom_project.manager


class Migration(migrations.Migration):

    replaces = [
        ('zoom_project', '0001_initial'), ('zoom_project', '0002_auto_20160930_1137'), ('zoom_project', '0003_auto_20161003_1151'), ('zoom_project', '0004_auto_20161027_1119'), ('zoom_project', '0005_auto_20170417_1508'), ('zoom_project', '0006_remove_zoomsettings_project'), ('zoom_project', '0007_auto_20170418_1514'), (
            'zoom_project',
            '0008_auto_20170419_1027',
        ), ('zoom_project', '0009_remove_zoomroom_settings'), ('zoom_project', '0010_auto_20170419_1530'), ('zoom_project', '0011_zoomsettings_project'), ('zoom_project', '0012_zoomsettings_rooms'), ('zoom_project', '0013_auto_20170425_1427'), ('zoom_project', '0014_auto_20170425_1428'), ('zoom_project', '0015_auto_20170710_0717'),
    ]

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('project', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZoomMeetingStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'created', model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, editable=False, verbose_name='created',
                    ),
                ),
                (
                    'modified', model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, editable=False, verbose_name='modified',
                    ),
                ),
                ('meeting_id', models.CharField(max_length=20)),
                ('meeting_uuid', models.CharField(max_length=50)),
                (
                    'status', models.CharField(
                        blank=True, choices=[
                            ('STARTED', 'Started'), ('ENDED', 'Ended'),
                        ], max_length=10, null=True,
                    ),
                ),
                ('host_id', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelManagers(
            name='zoommeetingstatus',
            managers=[
                ('objects', zoom_project.manager.ZoomMeetingStatusManager()),
            ],
        ),
        migrations.CreateModel(
            name='ZoomRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'created', model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, editable=False, verbose_name='created',
                    ),
                ),
                (
                    'modified', model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, editable=False, verbose_name='modified',
                    ),
                ),
                ('object_id', models.PositiveIntegerField()),
                ('meeting_id', models.CharField(blank=True, max_length=256, null=True, verbose_name='Meeting ID (Zoom)')),
                ('host_meeting_id', models.TextField(blank=True, null=True, verbose_name='Host Meeting ID (Zoom)')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Zoom Rooms',
                'verbose_name': 'Zoom Room',
            },
        ),
        migrations.CreateModel(
            name='ZoomSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'created', model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, editable=False, verbose_name='created',
                    ),
                ),
                (
                    'modified', model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, editable=False, verbose_name='modified',
                    ),
                ),
                ('zoom_api_key', models.CharField(max_length=256)),
                ('zoom_secret_key', models.CharField(max_length=256)),
                (
                    'project', models.OneToOneField(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.CASCADE, related_name='zoom_settings', to='project.Project',
                    ),
                ),
            ],
            options={
                'verbose_name_plural': 'Zooms Settings',
                'verbose_name': 'Zoom Settings',
            },
        ),
        migrations.AddField(
            model_name='zoomroom',
            name='_zoom_settings',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='rooms', to='zoom_project.ZoomSettings',
            ),
        ),
    ]