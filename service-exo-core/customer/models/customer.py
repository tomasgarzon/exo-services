from django.db import models

from entity.permissions import CustomerPermissionMixin
from entity.relations import CustomerUserRolesMixin
from entity.models import EntityMixin, ContactMixin
from permissions.models import BasePermissionsModel
from utils.models import TagAutoSlugField
from utils.images.fields import PowerImageField
from utils.mixins import LocationTimezoneMixin
from files.models import Resource

from ..managers.customer import CustomerManager
from ..conf import settings
from .customer_project_mixin import CustomerProjectMixin


class Customer(
        CustomerPermissionMixin,
        CustomerUserRolesMixin,
        EntityMixin,
        LocationTimezoneMixin,
        ContactMixin,
        CustomerProjectMixin,
        BasePermissionsModel
):

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='relation.CustomerUserRole',
        related_name='customers',
    )
    partners = models.ManyToManyField(
        'partner.Partner',
        through='relation.PartnerCustomerRole',
        related_name='customers',
    )
    profile_picture = PowerImageField(
        choice_field='selectable_profile_picture',
        thumbnails=settings.EXO_ACCOUNTS_DEFAULT_PICTURES_SIZES,
        upload_to='avatars',
        blank=True,
        null=True,
        verbose_name='profile picture',
    )
    selectable_profile_picture = models.CharField(
        max_length=255,
        choices=settings.CUSTOMER_IMAGE_CHOICES_PROFILE,
        blank=True,
        verbose_name='selected profile picture',
        default='theme/gallery/1.jpg',
        help_text='An image fallback when no profile picture uploaded',
    )
    customer_type = models.CharField(
        max_length=1,
        choices=settings.CUSTOMER_CH_TYPE_CUSTOMER,
        default=settings.CUSTOMER_CH_NORMAL,
    )

    slug = TagAutoSlugField(
        populate_from='name',
        always_update=True,
        null=True,
        blank=False,
        unique=True,
        tag_model=Resource,
    )
    objects = CustomerManager()

    class Meta:
        verbose_name_plural = 'Clients'
        verbose_name = 'Client'
        permissions = settings.CUSTOMER_ALL_PERMISSIONS
        ordering = ['name']

    class MetaPermissions:
        permissions_admin = settings.CUSTOMER_ADMIN_PERMISSIONS
        permissions_regular = settings.CUSTOMER_REGULAR_PERMISSIONS

    def __str__(self):
        return str('%s' % self.name)

    @property
    def training(self):
        return self.customer_type == settings.CUSTOMER_CH_TRAINING

    def set_partner(self, partner=None):
        if self.partners.first() != partner:
            self.partners.clear()
            self.partners_roles.create(
                partner=partner,
            )
