# Generated by Django 2.2.3 on 2019-08-01 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0014_conversation_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='_type',
            field=models.CharField(choices=[('O', 'Opportunities'), ('P', 'Project'), ('U', 'User 1 to 1')], max_length=1),
        ),
    ]