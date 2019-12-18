from django.db import models

from model_utils.models import TimeStampedModel

from ..conf import settings


class SocialNetwork(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='social_networks')
    network_type = models.CharField(
        max_length=1,
        choices=settings.EXO_ACCOUNTS_CH_SOCIAL_NETWORK)
    value = models.CharField(max_length=255)

    class Meta:
        db_table = 'accounts_socialnetworks'
        verbose_name_plural = 'SocialNetworks'
        verbose_name = 'SocialNetwork'

    def __str__(self):
        return self.value

    @property
    def is_filled(self):
        return self.value

    @property
    def is_website(self):
        return self.network_type == settings.EXO_ACCOUNTS_PERSONAL_WEBSITE

    @classmethod
    def is_link(cls, network_type):
        return network_type not in [settings.EXO_ACCOUNTS_SOCIAL_SKYPE]

    @property
    def is_social_network(self):
        # The name doesn't make sense, but we have some tools that they
        # are not really social network, like skype or your personal website.
        # If we have more than these, we should change the model
        return self.network_type not in [
            settings.EXO_ACCOUNTS_SOCIAL_SKYPE,
            settings.EXO_ACCOUNTS_PERSONAL_WEBSITE]

    @property
    def name(self):
        return self.get_network_type_display().lower()

    @property
    def name_value(self):
        return '{}.value'.format(self.name)
