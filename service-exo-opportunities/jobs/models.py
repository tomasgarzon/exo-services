from django.db import models


class Job(models.Model):
    uuid = models.UUIDField(
        blank=True, null=True)
    applicant = models.OneToOneField(
        'opportunities.Applicant',
        related_name='job',
        on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.uuid, self.applicant.user.uuid)
