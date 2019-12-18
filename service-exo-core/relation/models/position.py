from django.db import models


class UserPositionMixin(models.Model):
    position = models.CharField(
        'Position',
        blank=False, null=True,
        max_length=200,
        default='',
    )

    class Meta:
        abstract = True

    def get_current_position(self):
        return getattr(self, 'position', '')
