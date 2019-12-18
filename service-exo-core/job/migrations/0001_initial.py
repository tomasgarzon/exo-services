# Generated by Django 2.2.6 on 2019-10-14 12:24

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import utils.descriptors.choices_descriptor_mixin


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('category', models.CharField(choices=[('TI', 'Ticket'), ('PR', 'Project'), ('EP', 'ExOProject'), ('FA', 'Fastrack'), ('QA', 'QASession'), ('OP', 'Opportunity')], max_length=2)),
                ('status', models.CharField(choices=[('UP', 'Upcoming'), ('LI', 'Live'), ('IN', 'In Progress'), ('CO', 'Completed'), ('UN', 'Unknown')], default='UN', max_length=2)),
                ('title', models.CharField(blank=True, max_length=355, null=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('related_uuid', models.UUIDField()),
                ('role_code', models.CharField(max_length=3)),
                ('extra_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(utils.descriptors.choices_descriptor_mixin.ChoicesDescriptorMixin, models.Model),
        ),
    ]