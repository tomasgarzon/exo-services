import logging

# 3rd. libraries imports
from appconf import AppConf

# django imports
from django.conf import settings  # noqa

logger = logging.getLogger(__name__)


class QASessionConfig(AppConf):
    APP_NAME = 'qa_session'

    ABOUT_BEGIN = 'begin'
    ABOUT_END = 'end'

    CH_REALTIME_ACTIONS = (
        ABOUT_BEGIN,
        ABOUT_END
    )

    REALTIME_ABOUT_BEGIN = 10
    REALTIME_ABOUT_END = 10
