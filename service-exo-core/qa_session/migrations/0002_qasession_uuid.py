# Generated by Django 2.2.5 on 2019-09-30 10:26

from django.db import migrations, models
import uuid


def create_uuid(apps, schema_editor):
    QASession = apps.get_model('qa_session', 'qasession')
    for qasession in QASession.objects.all():
        qasession.uuid = uuid.uuid4()
        qasession.save(update_fields=['uuid'])


class Migration(migrations.Migration):

    dependencies = [
        ('qa_session', '0001_squashed_0006_auto_20180712_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='qasession',
            name='uuid',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.RunPython(create_uuid),
        migrations.AlterField(
            model_name='qasession',
            name='uuid',
            field=models.UUIDField(unique=True)
        )
    ]