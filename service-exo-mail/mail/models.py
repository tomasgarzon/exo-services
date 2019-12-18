from django.db import models
from django.db.models.signals import post_save

from mailer.models import Message


class MessageInfo(models.Model):
    subject = models.CharField(max_length=200)
    body = models.TextField()
    to_addresses = models.TextField()
    message = models.OneToOneField(
        'mailer.Message', related_name='info',
        on_delete=models.CASCADE)

    @property
    def to_addresses_as_list(self):
        return self.to_addresses.split(',')


def save_message_info(sender, instance, **kwargs):
    try:
        message_info = instance.info
    except Exception:
        message_info = MessageInfo(message=instance)

    message_info.subject = instance.email.subject
    message_info.body = instance.email.body
    message_info.to_addresses = ','.join(instance.email.to)
    message_info.save()


post_save.connect(save_message_info, sender=Message)
