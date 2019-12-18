from django.core.exceptions import ValidationError


from django.db import models
from django.contrib.postgres.fields import ArrayField

from model_utils.models import TimeStampedModel


class ProcessTemplateStepOption(TimeStampedModel):

    """
    Define options and custom methods for any RegistrationProcess
        - name: Readable name for the option
        - description: Description for the process or property defined
        - step_code: Step related to. If empty will apply to all steps
        - customizable: define if the option could be modified for each
            RegistrationProcess
        - method_name: full path of the method
        - method_kwargs: define parameters for the method
        - celery_task: [True/False]
        - celery_path: path for celery to execute
        - property_name: property name of the RegistrationProcess instance
        - property_value: default value for the property

    """
    name = models.CharField(
        max_length=200,
        blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    customizable = models.BooleanField(default=False)

    # Time execution
    pre_step = models.BooleanField()
    post_step = models.BooleanField()

    # Method option to call
    method_name = models.CharField(
        max_length=200,
        blank=True, null=True)
    method_kwargs = ArrayField(
        models.CharField(max_length=200),
        blank=True, null=True)

    # Property option
    property_name = models.CharField(
        max_length=200,
        blank=True, null=True)
    property_value = models.NullBooleanField()
    property_values = ArrayField(
        models.CharField(max_length=200),
        blank=True, null=True)

    # This fields will not be usable at StepOption
    OWN_FIELDS = ['customizable', ]

    def __str__(self):
        return '{} {} [{}]'.format(
            self.name,
            self.description,
            'M' if self.method_name else 'P',
        )

    def clean(self):
        msg = None
        if self.method_name == self.property_name and not self.method_name:
            msg = 'Define method or property name'

        if self.method_name is not None and self.property_name is not None:
            msg = "Couldn't define method_name and property_name"

        if msg:
            raise ValidationError(msg)

    def to_json(self, clean_own_fields=False):
        data = {}
        for field in self._meta.fields:
            if field.primary_key or field.name in self.OWN_FIELDS:
                continue
            data[field.name] = getattr(self, field.name)
        return data
