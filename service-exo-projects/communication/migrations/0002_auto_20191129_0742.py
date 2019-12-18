# Generated by Django 2.2.7 on 2019-11-29 07:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='team',
            field=models.OneToOneField(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='group', to='team.Team'),
        ),
    ]