from django.db import models
from django.utils.translation import ugettext_lazy as _

from permissions.models import BasePermissionsModel
from entity.permissions import PartnerPermissionMixin
from utils.models import TagAutoSlugField
from utils.images.fields import PowerImageField
from utils.mixins import LocationTimezoneMixin
from files.models import Resource

from ..manager import PartnerManager
from ..conf import settings


class Partner(
        PartnerPermissionMixin,
        LocationTimezoneMixin,
        BasePermissionsModel
):
    name = models.CharField(max_length=100, default='')

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='relation.PartnerUserRole',
        related_name='partners',
    )

    profile_picture = PowerImageField(
        choice_field='selectable_profile_picture',
        thumbnails=settings.EXO_ACCOUNTS_DEFAULT_PICTURES_SIZES,
        upload_to='avatars',
        blank=True,
        null=True,
        verbose_name=_('profile picture'),
    )
    selectable_profile_picture = models.CharField(
        max_length=255,
        choices=settings.CUSTOMER_IMAGE_CHOICES_PROFILE,
        blank=True,
        verbose_name=_('selected profile picture'),
        default='theme/gallery/1.jpg',
        help_text=_('An image fallback when no profile picture uploaded'),
    )
    slug = TagAutoSlugField(
        populate_from='name',
        always_update=True,
        null=True,
        blank=False,
        unique=True,
        tag_model=Resource,
    )
    objects = PartnerManager()

    class Meta:
        verbose_name_plural = 'Partners'
        verbose_name = 'Partner'
        permissions = settings.PARTNER_ALL_PERMISSIONS

    class MetaPermissions:
        permissions_admin = settings.PARTNER_ADMIN_PERMISSIONS
        permissions_regular = settings.PARTNER_REGULAR_PERMISSIONS

    def __str__(self):
        return str('%s' % self.name)
