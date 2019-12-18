from django.db import models


class Job(models.Model):
    uuid = models.UUIDField(
        blank=True, null=True)
    participant = models.OneToOneField(
        'event.Participant',
        related_name='job',
        on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.uuid, self.participant)
