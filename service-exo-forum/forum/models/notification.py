from django.db import models


class NotificationSettingsCategory(models.Model):
    category = models.OneToOneField(
        'Category',
        related_name='settings')
    new_post = models.CharField(
        blank=True, null=True,
        max_length=200)
    new_answer = models.CharField(
        blank=True, null=True,
        max_length=200)
    new_mention = models.CharField(
        blank=True, null=True,
        max_length=200)
    update_post = models.CharField(
        blank=True, null=True,
        max_length=200)
