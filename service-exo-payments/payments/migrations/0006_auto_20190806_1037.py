# Generated by Django 2.2.4 on 2019-08-06 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0005_auto_20190611_1832'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='amount_eur',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='rate',
            field=models.FloatField(blank=True, null=True),
        ),
    ]