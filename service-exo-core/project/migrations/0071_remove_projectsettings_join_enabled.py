# Generated by Django 2.2.7 on 2019-11-14 10:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0070_auto_20191113_1502'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectsettings',
            name='join_enabled',
        ),
    ]