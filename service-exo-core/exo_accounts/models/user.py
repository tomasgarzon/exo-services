import warnings
import uuid
import logging

from django.apps import apps
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core import signing
from autoslug import AutoSlugField
from password_reset import views
from guardian.mixins import GuardianUserMixin

from permissions.models import PermissionManagerMixin
from utils.mixins import LocationTimezoneMixin
from utils.images.fields import PowerImageField

from ..conf import settings
from ..helpers import calculate_user_position
from ..manager import UserManager
from ..permissions import BaseUserPermission
from ..signals_define import (signal_password_updated,
                              signal_exo_user_request_new_password)
from ..utils import toHex
from ..utils.models import UniqueNameMixin, CollectInstancesRelatedMixin
from .mixins import (
    UserCacheMixin,
    UserLanguageMixin,
    UserProfileMixin,
    SocialNetworkMixin,
    IntercomUserMixin,
    UserAgreementMixin,
    UserInvitationMixin,
    UserSectionsMixin)

logger = logging.getLogger('user')


class User(
        PermissionsMixin,
        BaseUserPermission,
        PermissionManagerMixin,
        UserProfileMixin,
        LocationTimezoneMixin,
        AbstractBaseUser,
        SocialNetworkMixin,
        views.SaltMixin,
        GuardianUserMixin,
        UniqueNameMixin,
        CollectInstancesRelatedMixin,
        UserCacheMixin,
        UserLanguageMixin,
        IntercomUserMixin,
        UserAgreementMixin,
        UserInvitationMixin,
        UserSectionsMixin):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False)

    password_updated = models.BooleanField(default=False)

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True
    )
    short_name = models.CharField(
        _('Short name'),
        max_length=100,
        blank=True,
        null=True)
    full_name = models.CharField(
        _('Full name'),
        max_length=255,
        blank=True,
        null=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    slug = AutoSlugField(
        populate_from='get_full_name',
        always_update=False,
        null=True,
        blank=True,
        unique=True)

    profile_picture = PowerImageField(
        backgrounds=settings.EXO_ACCOUNTS_PROFILE_COLOR_BACKGROUND,
        thumbnails=settings.EXO_ACCOUNTS_PROFILE_PICTURE_SIZES,
        upload_to='avatars',
        blank=True,
        null=True,
        verbose_name=_('profile picture'),
    )
    profile_picture_origin = models.CharField(
        max_length=1,
        choices=settings.EXO_ACCOUNTS_PROFILE_PICTURE_ORIGIN_CHOICES,
        default=settings.EXO_ACCOUNTS_PROFILE_PICTURE_CH_DEFAULT)
    _username = models.CharField(
        blank=True, null=True,
        max_length=150,
        unique=True)
    user_title = models.TextField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    ALTERNATIVE_USERNAME_FIELD = 'uuid'
    REQUIRED_FIELDS = []
    SEARCHEABLE_FIELDS = ['full_name', 'short_name']

    class Meta:
        db_table = 'accounts_user'
        verbose_name_plural = 'Users'
        verbose_name = 'User'
        permissions = settings.EXO_ACCOUNTS_ALL_PERMISSIONS

    def __str__(self):
        full_name = self.get_full_name()
        if not full_name:
            return self.email
        return full_name

    @property
    def is_admin(self):
        """
        Is the user admin?
        Simplest possible answer: all superuser are admin
        """
        return self.is_superuser

    @property
    def is_consultant(self):
        return getattr(self, 'consultant', None) is not None

    def is_empty_user(self):
        """
        An "EmptyUser" is an user that is not a Consultant or Participant
        """
        empty_classes = {
            apps.get_model(app[0], app[1]) for app in settings.EXO_ACCOUNTS_EMPTY_USER_CLASSES
        }

        user_related_classes = {
            _ for _ in self.get_instances_related().data.keys()
        }

        return not self.is_admin and \
            not self.is_staff and \
            user_related_classes == empty_classes

    def get_user_empty_classes(self):
        empty_classes = {
            apps.get_model(app[0], app[1])
            for app in settings.EXO_ACCOUNTS_EMPTY_USER_CLASSES
        }
        return [_ for _ in self.get_instances_related().data.keys()
                if _ in empty_classes]

    def has_certified_role(self, code):
        has_certified_role = None

        if self.is_consultant:
            has_certified_role = self.consultant.certification_roles.filter(
                code=code).exists()

        return has_certified_role

    @property
    def is_customer(self):
        return self.customers_roles \
            .filter(user=self) \
            .filter(status=settings.RELATION_ROLE_CH_ACTIVE) \
            .count() > 0

    @property
    def display_leftmenu(self):
        """
        Users that will use the FrontEnd left Menu
        """
        return True

    @property
    def customer(self):
        customer = None

        if self.is_customer:
            customer = self.customers_roles \
                .filter(user=self) \
                .filter(status=settings.RELATION_ROLE_CH_ACTIVE)[0].customer

        return customer

    @property
    def can_authenticate(self):
        """
        A user can authenticate when is active and has a usable password
        """
        return self.is_active and self.has_usable_password()

    @property
    def username(self):
        return getattr(self, self.USERNAME_FIELD)

    def get_full_name(self):
        # The user is identified by their email address
        if self.full_name:
            return self.full_name
        return self.get_short_name()

    def get_short_name(self):
        # The user is identified by their email address
        return self.short_name

    @property
    def first_name(self):
        warnings.warn(
            'first_name and last name are deprecated. '
            'You should use short_name and full_name',
            DeprecationWarning)
        return self.get_short_name()

    @property
    def last_name(self):
        warnings.warn(
            'first_name and last name are deprecated. '
            'You should use short_name and full_name',
            DeprecationWarning)
        return self.get_full_name()

    def add_email_address(self, email, verified=False):
        """
            Add a new email address to user
        """
        return self.emailaddress_set.add_email(self, email, verified)

    def get_public_url(self, invitation):
        return ''

    @property
    def profile_pictures(self):
        profile_pictures = []

        class UserProfilePicture:
            width = None
            height = None
            url = None

        for width, height in self._meta.get_field('profile_picture').thumbnails:
            value = UserProfilePicture()
            value.width = width
            value.height = height
            value.url = self.profile_picture.get_thumbnail_url(width, height)
            profile_pictures.append(value)

        return profile_pictures

    @staticmethod
    def fullname():
        return 'short_name', 'full_name'

    def get_letter_initial(self):
        if self.short_name:
            initial = self.short_name[:2].upper()
        else:
            initial = self.username[:2].upper()
        return initial

    @property
    def public_username(self):
        return self._username

    @public_username.setter
    def public_username(self, name):
        self._username = self.create_unique(
            value=name,
            name_field='_username',
            suffix='%s')
        self.save(update_fields=['_username'])

    def generate_public_username(self):
        full_name = self.get_full_name()
        name = slugify(full_name).replace('-', '.')
        self.public_username = name

    @property
    def public_email(self):
        if self.is_consultant:
            suffix = settings.EXO_CONSULTANT_DOMAIN
        else:
            suffix = settings.EXO_USER_DOMAIN

        exo_account = self.emailaddress_set.exo_account()
        if exo_account:
            return exo_account.email
        else:
            alias = self.public_username

        return '{}@{}'.format(alias, suffix)

    def send_notification_change_password(self, email_to=None):

        token = signing.dumps(self.pk, salt=self.salt)
        send_to = email_to or self.email
        cipher_email = toHex(send_to)

        signal_exo_user_request_new_password.send(
            sender=self.__class__,
            recipients=[send_to],
            token=token,
            cipher_email=cipher_email,
            name=self.get_short_name())

        logger.info('User notification to change password: {}'.format(self.email))

    def set_password(self, raw_password, random_password=False):
        super().set_password(raw_password)
        if raw_password:
            self.password_updated = not random_password
            if self.pk:
                self.save(update_fields=['password_updated'])
            signal_password_updated.send_robust(
                sender=User,
                instance=self,
                password=raw_password)

    def set_unusable_password(self):
        # Set a value that will never be a valid hash
        super().set_unusable_password()
        self.password_updated = False
        if self.pk:
            self.save(update_fields=['password_updated'])

    def accept(self, user_from, **kwargs):
        """
        If password is None the user comes form an external Authentication service
        and we set an unusable password.
        Kwargs params:
                - email: email for this user
                - password: user password or None

        """
        random_password = False
        email = kwargs.get('email', None)

        password = kwargs.get('password', None)
        if not password:
            password = User.objects.make_random_password()
            random_password = True

        self.set_password(password, random_password)
        self.save()

        if email and self.email != email:
            email_address = self.emailaddress_set.filter(email=email).first()
            if email_address and email_address.is_verified:
                self.email = email
            else:
                self.add_email_address(email)
        self.save()

    def send_notification(self, invitation):
        logger.info('User Invitation Signup: {}'.format(invitation.user.email))

    @property
    def has_profile_picture_default(self):
        return self.profile_picture_origin == settings.EXO_ACCOUNTS_PROFILE_PICTURE_CH_DEFAULT

    def belongs_to_hub(self, hub_type):
        return self.hubs.filter(hub___type=hub_type).exists()

    @property
    def user_position(self):
        return calculate_user_position(self)

    def get_badges(self, code=None):
        badges = self.badge_userbadge_related.all()

        if code:
            badges = badges.filter(badge__code=code)

        return badges.order_by('badge__order')
