from django.db import models
from django.conf import settings
from django.utils.html import format_html


class CreatedByMixin(models.Model):

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_related',
        null=True, blank=True,
    )

    class Meta:
        abstract = True


class EmailMixin(models.Model):

    email_status = models.CharField(max_length=20, default='Pending')
    email_url = models.URLField(
        max_length=512,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    @property
    def email_link_tag(self):
        link = '-'
        if self.email_url:
            link = format_html(
                '<a href="{}" target="blank">Email Link</a>',
                self.email_url,
            )

        return link
