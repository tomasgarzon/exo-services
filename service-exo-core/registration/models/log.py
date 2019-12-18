from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import date as date_format

from model_utils.models import TimeStampedModel


class RegistrationLog(TimeStampedModel):
    """
        Complete LogField for changes on the Registration Process
    """
    process = models.ForeignKey(
        'RegistrationProcess',
        related_name='logs',
        on_delete=models.CASCADE)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    text = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=100,
        blank=True, null=True)
    display_status = models.CharField(
        max_length=100,
        blank=True, null=True)
    display = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        log = ''
        if self.display:
            log = '{} {} at {}'.format(
                self.text,
                self.display_status,
                date_format(self.date).capitalize(),
            )
        return log

    @property
    def type_object(self):
        type_object = self.text
        if hasattr(self.content_object, 'validation'):
            type_object = self.content_object.validation.frontend_name

        return type_object

    @property
    def frontend_message(self):
        try:
            type_object = self.type_object
        except ValueError:
            type_object = ''

        return '{} {} on {}'.format(
            type_object,
            self.display_status,
            date_format(self.date).capitalize(),
        )
