from django.conf import settings
from django.db import models

from model_utils.models import TimeStampedModel

from custom_auth.helpers import UserProfileWrapper
from exo_certification.api.serializers.certification_role import CertificationRoleSerializer

from .managers import MemberManager


class Member(TimeStampedModel):
    num_projects = models.IntegerField(db_index=True, default=0)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ecosystem_member',
    )

    objects = MemberManager()

    def __str__(self):
        return self.full_name

    def update_activity(self):
        update_fields = ['modified', 'num_projects']
        self.update_num_projects(commit=False)
        return self.save(update_fields=update_fields)

    def update_num_projects(self, commit=True):
        self.num_projects = self.user.get_all_projects().count()
        if commit:
            self.save(update_fields=['num_projects'])

    @property
    def _profile(self):
        return UserProfileWrapper(user=self.user)

    @property
    def _consultant(self):
        return self.user.consultant

    @property
    def full_name(self):
        return self.user.full_name

    @property
    def user_title(self):
        return self.user.user_title

    @property
    def user_position(self):
        return self.user.user_position

    @property
    def is_staff(self):
        return self._profile.is_openexo_member

    @property
    def is_active(self):
        return self._consultant.is_active

    @property
    def slug(self):
        return self.user.slug

    @property
    def certifications(self):
        return CertificationRoleSerializer(
            self.user.consultant.certification_roles.all(),
            many=True,
            context={'user': self.user}
        ).data

    @property
    def profile_pictures(self):
        return self.user.profile_pictures

    @property
    def registered(self):
        return self.user.date_joined

    @property
    def last_activity(self):
        return self.modified

    @property
    def location(self):
        return self.user.location

    @property
    def languages(self):
        return self.user.consultant.languages.all()
