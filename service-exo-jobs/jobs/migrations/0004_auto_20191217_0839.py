# Generated by Django 2.2.8 on 2019-12-17 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_auto_20191216_1219'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='related_class',
            field=models.CharField(
                blank=True,
                choices=[('CP', 'CoreProject'), ('CX', 'ExOProject'), ('CO', 'Opportunity'), ('CE', 'Event')],
                max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='related_uuid',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]