from django.db import models


class ContactMixin(models.Model):
    contact_person = models.TextField(blank=True, null=True)
    phone = models.CharField(blank=True, null=True, max_length=20)
    website = models.CharField(blank=True, null=True, max_length=300)
    address = models.CharField(blank=True, null=True, max_length=100)
    postcode = models.CharField(blank=True, null=True, max_length=10)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    google = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    blog = models.URLField(blank=True, null=True)

    class Meta:
        abstract = True
