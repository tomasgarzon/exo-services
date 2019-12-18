# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-07-09 06:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import qa_session.managers.qa_session
import qa_session.managers.qa_session_team
import utils.models.timezone_field


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('team', '0001_squashed_0010_auto_20170710_0717'),
        ('project', '0046_auto_20190710_0710'),
        ('relation', '0002_hubuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='QASession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(
                    default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(
                    default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('start_at', models.DateTimeField()),
                ('end_at', models.DateTimeField()),
                ('timezone', utils.models.timezone_field.TimeZoneField()),
                ('advisors', models.ManyToManyField(related_name='qa_sessions', to='relation.ConsultantProjectRole')),
                ('created_by', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                    related_name='qa_session_qasession_related', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='qa_sessions', to='project.Project')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QASessionTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(
                    default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(
                    default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('created_by', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                    related_name='qa_session_qasessionteam_related', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='teams', to='qa_session.QASession')),
                ('team', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, related_name='qa_sessions', to='team.Team')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='qasession',
            name='timezone',
        ),
        migrations.AlterModelManagers(
            name='qasession',
            managers=[
                ('objects', qa_session.managers.qa_session.QASessionManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='qasessionteam',
            managers=[
                ('objects', qa_session.managers.qa_session_team.QASessionTeamManager()),
            ],
        ),
        migrations.AddField(
            model_name='qasession',
            name='name',
            field=models.CharField(default='Swarm Session', max_length=200),
        ),
        migrations.AlterModelOptions(
            name='qasession',
            options={'ordering': ['start_at']},
        ),
        migrations.AlterModelOptions(
            name='qasessionteam',
            options={'ordering': ['session__start_at']},
        ),
    ]