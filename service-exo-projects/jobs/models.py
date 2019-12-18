from django.db import models


class Job(models.Model):
    uuid = models.UUIDField(
        blank=True, null=True)
    user_project_role = models.OneToOneField(
        'project.UserProjectRole',
        related_name='job',
        on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.uuid, self.user_project_role.user.uuid)
