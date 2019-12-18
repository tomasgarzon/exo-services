from django.db import models

from .conf import settings


class EntityMixin(models.Model):
    name = models.CharField('Organization Name', max_length=100)
    description = models.TextField(
        'Description',
        blank=True, null=True,
    )
    size = models.CharField(
        max_length=1,
        blank=False, null=True,
        choices=settings.ENTITY_CH_ORGANIZATION_SIZE,
    )
    annual_revenue = models.BigIntegerField(null=True, blank=True)
    market_value = models.BigIntegerField(null=True, blank=True)
    industry = models.ForeignKey(
        'industry.Industry',
        models.SET_NULL,
        blank=False, null=True,
    )

    class Meta:
        abstract = True


class ContactMixin(models.Model):
    phone = models.CharField(
        'Phone',
        blank=True, null=True,
        max_length=20,
    )
    website = models.CharField(
        'Website',
        blank=True, null=True,
        max_length=300,
    )
    address = models.CharField(
        'Address',
        blank=True, null=True,
        max_length=100,
    )
    postcode = models.CharField(
        'Postcode',
        blank=True, null=True,
        max_length=10,
    )
    contact_person = models.TextField(
        'Contact Person',
        blank=True, null=True,
    )
    facebook = models.URLField(
        'Facebook',
        blank=True, null=True,
    )
    twitter = models.URLField(
        'Twitter',
        blank=True, null=True,
    )
    google = models.URLField(
        'Google +',
        blank=True, null=True,
    )
    linkedin = models.URLField(
        'Linkedin',
        blank=True, null=True,
    )
    blog = models.URLField(
        'Blog',
        blank=True, null=True,
    )

    class Meta:
        abstract = True

    def full_address(self):
        full_address = [self.address, self.postcode, self.city, self.get_country_display()]
        return ', '.join([k for k in full_address if k])

    @property
    def empty_contact_info(self):
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if value:
                return False
        return True
