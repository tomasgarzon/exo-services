# Generated by Django 2.2.2 on 2019-06-07 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunities', '0016_auto_20190605_1522'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='applicantsow',
            name='due_date',
        ),
        migrations.RemoveField(
            model_name='applicantsow',
            name='duration',
        ),
        migrations.AddField(
            model_name='applicantsow',
            name='end_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='applicantsow',
            name='start_date',
            field=models.DateField(null=True),
        ),
    ]