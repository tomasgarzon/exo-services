from django.db import models

from ...conf import settings


class UserProfileMixin(models.Model):
    about_me = models.TextField(blank=True, null=True)
    bio_me = models.TextField(blank=True, null=True)
    short_me = models.TextField(blank=True, null=True)
    phone = models.CharField('Phone', blank=True, null=True, max_length=50)
    email_contact = models.EmailField(blank=True, null=True)
    _platform_language = models.CharField(
        blank=False, null=False,
        max_length=8,
        default=settings.EXO_ACCOUNTS_LANGUAGE_DEFAULT,
        choices=settings.EXO_ACCOUNTS_LANGUAGES)

    class Meta:
        abstract = True

    def _get_projects(self):
        queryset = self.projects_member.actives().only_visible()
        return queryset.projects()

    def get_projects(self):
        if self.is_consultant:
            return self.consultant.get_projects()
        else:
            return self._get_projects()

    def get_all_projects(self):
        projects = self._get_projects()
        if self.is_consultant:
            projects |= self.consultant.get_projects()

        return projects.distinct()

    @property
    def segment(self):
        if self.is_consultant:
            return settings.EXO_ACCOUNTS_SEGMENT_CONSULTANT
        elif self.is_customer:
            return settings.EXO_ACCOUNTS_SEGMENT_CUSTOMER
        else:
            return settings.EXO_ACCOUNTS_SEGMENT_STAFF

    def save(self, *args, **kwargs):
        if 'update_fields' in kwargs and kwargs['update_fields'] == ['last_login']:
            self._meta.base_manager.filter(pk=self.pk).update(
                last_login=self.last_login)
            return self
        return super().save(*args, **kwargs)
