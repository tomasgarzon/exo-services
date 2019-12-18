from appconf import AppConf

from django.conf import settings  # noqa


class EcosystemConfig(AppConf):
    APP_NAME = 'ecosystem'

    API_STATUS_ALL = 'E'
    API_STATUS_ACTIVE = 'A'
    API_STATUS_INACTIVE = 'D'
