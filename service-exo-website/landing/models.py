from django.db import models

from model_utils.models import TimeStampedModel

from .conf import settings


class Page(TimeStampedModel):
    uuid = models.UUIDField(unique=True)
    page_type = models.CharField(
        max_length=200,
        default=settings.LANDING_CH_TYPE_DEFAULT,
        choices=settings.LANDING_CH_PAGE_TYPES)
    theme = models.CharField(
        max_length=100, default=settings.LANDING_CH_THEME_DEFAULT,
        choices=settings.LANDING_CH_THEMES)
    slug = models.CharField(
        max_length=200, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        on_delete=models.SET_NULL)
    published = models.BooleanField(
        default=False)

    def __str__(self):
        return "{}: {} {}".format(self.uuid, self.theme, self.slug)

    def mark_as_published(self):
        self.published = True
        self.save()

    @property
    def link(self):
        return "{}/{}/".format(settings.EXO_WEBSITE_DOMAIN, self.slug)

    @property
    def link_preview(self):
        return "{}/{}-preview/".format(settings.EXO_WEBSITE_DOMAIN, self.slug)


class Section(TimeStampedModel):
    page = models.ForeignKey(
        'Page', related_name='sections',
        on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content = models.TextField()
    index = models.IntegerField()

    class Meta:
        ordering = ['index']

    def __str__(self):
        return "Section {}".format(self.index)
