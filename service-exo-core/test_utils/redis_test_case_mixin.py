# Third Party Library
from .pytest import bootstrap


class RedisTestCaseMixin:

    """
        TestCase class that clears the database between the tests
    """

    def _pre_setup(self):
        bootstrap.redis_clear()
        super(RedisTestCaseMixin, self)._pre_setup()
