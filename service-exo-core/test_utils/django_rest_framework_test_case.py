# Third Party Library
from rest_framework.test import APITestCase, APILiveServerTestCase

from .redis_test_case_mixin import RedisTestCaseMixin


class DjangoRestFrameworkTestCase(
        RedisTestCaseMixin,
        APITestCase,
):
    """
    Class for testing Django rest framework entry points
    """
    pass


class DjangoRestFrameworkLiveTestCase(APILiveServerTestCase):
    """
    Class for testing Django rest framework entry points with LiveServer
    serialized_rollback: https://docs.djangoproject.com/en/1.8/topics/testing/overview/#rollback-emulation
    """
    serialized_rollback = True
