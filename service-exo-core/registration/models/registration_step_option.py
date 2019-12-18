from django.db import models
from django.contrib.postgres.fields import ArrayField

from model_utils.models import TimeStampedModel


class StepOption(TimeStampedModel):
    name = models.CharField(
        max_length=200,
        blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Time execution
    pre_step = models.NullBooleanField()
    post_step = models.NullBooleanField()

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

    def __str__(self):
        return '{}: {}'.format(self.name, self.description)

    @classmethod
    def reset(cls, option_obj, *args, **kwargs):
        """
        Receive an instance of an ProcessTemplateStepOption object
        """
        step_option = cls()
        list(map(lambda x: setattr(step_option, x[0], x[1]), option_obj.to_json(True).items()))
        step_option.save()
        return step_option
