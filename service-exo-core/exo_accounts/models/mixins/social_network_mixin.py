from django.conf import settings


class SocialDescriptor(object):
    def __init__(self, social):
        self.social = social

    def __get__(self, obj, objtype):
        return self.social

    def __set__(self, obj, val):
        self.social.value = val
        self.social.save()


class SocialNetworkMixin:
    """
        Mixin to manage social network for an User
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.initialize_social_networks()

    def initialize_social_networks(self):
        social_networks = self.social_networks.filter(
            network_type__in=settings.EXO_ACCOUNTS_SOCIAL_TYPES)
        social_exists = []
        for social in social_networks:
            name = social.get_network_type_display().lower()
            descriptor = SocialDescriptor(social)
            setattr(self.__class__, name, descriptor)
            social_exists.append(social.network_type)
        for key, value in settings.EXO_ACCOUNTS_CH_SOCIAL_NETWORK:
            if key in social_exists:
                continue

            name = value.lower()
            social = self.social_networks.model(network_type=key, user=self)
            descriptor = SocialDescriptor(social)
            setattr(self.__class__, name, descriptor)

    def create_social_network(self, network_type, value):
        return self.social_networks.create(network_type=network_type, value=value)

    def update_social_network(self, network_type, value):
        try:
            social = self.social_networks.get(network_type=network_type)
        except self.social_networks.model.DoesNotExist:
            return None
        social.value = value
        social.save(update_fields=['value'])
        return social

    def delete_social_network(self, network_type):
        try:
            social = self.social_networks.get(network_type=network_type)
        except self.social_networks.model.DoesNotExist:
            return None
        social.delete()

    def social_network_linkedin(self):
        try:
            social = self.social_networks.get(
                network_type=settings.EXO_ACCOUNTS_SOCIAL_LINKEDIN)
        except self.social_networks.model.DoesNotExist:
            return None
        return social.value

    def get_social_by_type(self, network_type):
        try:
            return self.social_networks.get(
                network_type=network_type)
        except self.social_networks.model.DoesNotExist:
            return self.social_networks.create(network_type=network_type)

    def build_social_network(self):
        social_list = []
        has_filled = False
        for key, value in settings.EXO_ACCOUNTS_CH_SOCIAL_NETWORK:
            social = self.get_social_by_type(key)
            if social.pk:
                has_filled = True
            social_list.append(social)
        return has_filled, social_list
