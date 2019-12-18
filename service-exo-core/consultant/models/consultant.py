from django.db import models

from model_utils.models import TimeStampedModel
from multiselectfield import MultiSelectField

from agreement.mixins import AgreementMixin
from permissions.models import PermissionManagerMixin
from registration.models import RegistrationProcess
from utils.models import CollectInstancesRelatedMixin
from utils.descriptors import ChoicesDescriptorMixin
from utils.dates import find_timezone
from invitation.models import Invitation
from custom_auth.helpers import UserProfileWrapper
from custom_auth.tasks.user_location import UserLocationTask

from .mixins import ConsultantCacheMixin
from ..managers.consultant import ConsultantManager, AllConsultantManager
from ..conf import settings
from .consultant_access_mixin import ConsultantAccessMixin


class Consultant(
        PermissionManagerMixin,
        ChoicesDescriptorMixin,
        ConsultantAccessMixin,
        ConsultantCacheMixin,
        AgreementMixin,
        TimeStampedModel,
        CollectInstancesRelatedMixin
):

    CH_STATUS = settings.CONSULTANT_STATUS_CH_STATUS

    status = models.CharField(
        'Consultant status',
        blank=False, null=False,
        max_length=1,
        default=settings.CONSULTANT_STATUS_DEFAULT,
        choices=CH_STATUS,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consultant',
    )

    languages = models.ManyToManyField(
        'core.Language',
        blank=True,
    )

    _industries = models.ManyToManyField(
        'industry.Industry',
        related_name='_consultants',
        through='relation.ConsultantIndustry',
    )

    _exo_attributes = models.ManyToManyField(
        'exo_attributes.ExOAttribute',
        related_name='_consultants',
        through='relation.ConsultantExOAttribute',
    )
    _exo_areas = models.ManyToManyField(
        'exo_area.ExOArea',
        related_name='_consultants',
        through='relation.ConsultantExOArea',
    )
    _keywords = models.ManyToManyField(
        'keywords.Keyword',
        related_name='_consultants',
        through='relation.ConsultantKeyword',
    )

    primary_phone = models.CharField(
        'Primary Phone',
        blank=True, null=True,
        max_length=50,
    )

    secondary_phone = models.CharField(
        'Phone Number 2',
        blank=True, null=True,
        max_length=50,
    )

    public_sites = MultiSelectField(
        choices=settings.CONSULTANT_PUBLIC_SITES,
        blank=True, null=True,
    )

    # Delete
    web_status = models.CharField(
        'Consultant Public web status',
        blank=False, null=False,
        max_length=1,
        default=settings.CONSULTANT_STATUS_DEFAULT,
        choices=settings.CONSULTANT_WEB_CH_STATUS,
    )

    certification_roles = models.ManyToManyField(
        'exo_role.CertificationRole',
        through='relation.ConsultantRole',
        related_name='certification_roles',
        blank=True,
    )

    objects = ConsultantManager()
    all_objects = AllConsultantManager()

    class Meta:
        verbose_name_plural = 'Consultants'
        verbose_name = 'Consultant'
        permissions = settings.CONSULTANT_ALL_PERMISSIONS
        ordering = ['user__short_name']

    def __str__(self):
        return str('%s - %s' % (self.user, self.user.email))

    @property
    def showing_web(self):
        return self.public_sites

    @showing_web.setter
    def showing_web(self, value):
        if value not in dict(settings.CONSULTANT_PUBLIC_SITES):
            raise ValueError('Invalid site definition')

        if value in self.showing_web:
            self.public_sites.remove(value)
        else:
            self.public_sites.append(value)
        self.save(update_fields=['public_sites', 'modified'])

    @property
    def agreement(self):
        """
            Get the latest Agreement for this user
        """
        return self.user.agreements.latest('agreement__version')

    @property
    def social_networks(self):
        return self.user.social_networks.all()

    @property
    def registration_process(self):
        registration = None
        try:
            registration = self.user.registration_process
        except RegistrationProcess.DoesNotExist:
            pass
        return registration

    @property
    def has_registration_process_finished(self):
        return\
            (not self.registration_process) \
            or (self.registration_process and self.registration_process.is_registered)

    @property
    def registration_process_current_url(self):
        invitation = self.registration_process.current_step.invitation
        return invitation.validation_object.get_public_url(invitation)

    @property
    def is_exo_certified(self):
        return self.consultant_roles.all().exists()

    @property
    def total_keywords_attributes_industries(self):
        return self.industries.at_least_minium_level(
        ).count()\
            + self.keywords.at_least_minium_level().count()\
            + self.exo_attributes.at_least_minium_level().count()

    @property
    def is_in_waiting_list(self):
        return self.user.groups.filter(
            name=settings.CONSULTANT_WAITING_LIST_GROUP_NAME).exists()

    def get_pending_validations(self):
        return self.validations.filter(
            status__in=[
                settings.CONSULTANT_VALIDATION_CH_PENDING_REVIEW,
                settings.CONSULTANT_VALIDATION_CH_SENT_SKIPPED,
                settings.CONSULTANT_VALIDATION_CH_WAITING,
                settings.CONSULTANT_VALIDATION_CH_SENT,
            ],
        )

    def channel_partner(self):
        return self.user.partners_roles.actives()

    def get_full_name(self):
        return self.user.get_full_name()

    def get_short_name(self):
        return self.user.get_short_name()

    def get_current_position(self):
        try:
            return self.user.partners_roles.actives()[0].get_current_position()
        except IndexError:
            pass
        return self.user._position

    def _roles(self, exo_role=None):
        queryset = self.roles.actives()
        if exo_role:
            queryset = queryset.filter_by_exo_role(exo_role)
        return queryset

    def get_projects(self, exo_role=None):
        queryset = self._roles(exo_role).only_visible()
        return queryset.projects()

    def add_validation(
        self, user_from, validation_name,
        custom_text=None, *args, **kwargs
    ):
        return self.validations.create_validation_by_name(
            user_from, validation_name, custom_text=custom_text,
            *args, **kwargs
        )

    def can_activate(self, user_from):
        """
        Check who can activate the user object
        """
        return True

    def can_deactivate(self, user_from):
        """
        Check who can deactivate the user object
        """
        return True

    def activate(self, user_from):
        """
        Activates an Inactive User
        """
        self.user.activate(user_from)

    def deactivate(self, user_from, description=None):
        """
        Deactivate the User
        """
        self.user.deactivate(user_from)

    def accept(self, user_from, **kwargs):
        user = self.user
        if kwargs.get('profile_picture'):
            content_file = kwargs.get('profile_picture')
            user.profile_picture.save(
                content_file.name,
                content_file, False
            )
            user.profile_picture_origin = settings.EXO_ACCOUNTS_PROFILE_PICTURE_CH_USER

        user.full_name = kwargs.get('full_name')
        user.short_name = kwargs.get('short_name')
        user.location = kwargs.get('location')
        place_id = kwargs.get('place_id')
        if place_id:
            user.place_id = place_id
            user.timezone = find_timezone(place_id)
        user.short_me = kwargs.get('short_me', user.short_me)
        user.about_me = kwargs.get('about_me', user.about_me)
        user.bio_me = kwargs.get('bio_me', user.bio_me)
        user.slug = user.get_full_name()
        user.save()
        UserLocationTask().s(
            user_id=user.pk).apply_async()

        self.languages.set(kwargs.get('languages', []))
        self.exo_profile.exo_activities.update_from_values(
            consultant_profile=self.exo_profile,
            exo_activities=kwargs.get('exo_activities', []),
        )
        self.exo_profile.set_contracting(**kwargs.get('contracting_data', {}))
        self.exo_profile.set_personal_mtp(kwargs.get('personal_mtp', ''))
        self.exo_areas.update_from_values(self, kwargs.get('areas', []))

    def cancel(self, user_from, description):
        pass

    @property
    def status_detail(self):
        status = None
        own_status = self.get_status_display()
        if self.is_disabled:
            return own_status
        try:
            if not self.registration_process.is_registered:
                status = self.registration_process.current_step.code
        except AttributeError:
            pass
        if status:
            return status
        return own_status

    def disable(self, user_from):
        self.deactivate(user_from)
        validations = self.get_pending_validations()
        for validation in validations:
            try:
                invitation = Invitation.objects.filter_by_object(validation)[0]
            except Invitation.DoesNotExist:
                invitation = None
            if invitation:
                invitation.cancel(user_from)
        self.status = settings.CONSULTANT_STATUS_CH_DISABLED
        self.save(update_fields=['status'])

    def reactivate(self, user_from):
        self.activate(user_from)
        registration = self.registration_process
        if registration:
            if registration.is_registered:
                status = settings.CONSULTANT_STATUS_CH_ACTIVE
                self.user.send_notification_change_password()
            else:
                registration.resume()
                last_validation = registration.current_step.content_object
                invitation = Invitation.objects.filter_by_object(last_validation).first()
                if invitation:
                    invitation.reactivate(user_from)
                status = settings.CONSULTANT_STATUS_CH_PENDING_VALIDATION
        else:
            RegistrationProcess._create_process(
                user_from=user_from,
                user=self.user,
            )
            status = settings.CONSULTANT_STATUS_CH_PENDING_VALIDATION
        self.status = status
        self.save(update_fields=['status'])

    def get_public_profile_v2(self):
        return UserProfileWrapper(self.user).profile_slug_url

    def get_certificates(self):
        consultant_roles = self.consultant_roles.all().distinct()

        return self.user.certifications.filter(
            status=settings.CERTIFICATION_CH_STATUS_GENERATED,
            consultant_roles__in=consultant_roles).order_by('group__name')
