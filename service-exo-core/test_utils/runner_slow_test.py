from rainbowtests.test.runner import RainbowDiscoverRunner
from rainbowtests import messages

from .test_runner_result import TimeLoggingTestRunner

DEFAULT_TEST_THRESHOLD = 2.0


class SlowTestRunner(RainbowDiscoverRunner):
    test_runner = TimeLoggingTestRunner

    def __init__(self, slow_test_threshold=DEFAULT_TEST_THRESHOLD, *args, **kwargs):
        self.slow_test_threshold = slow_test_threshold
        super().__init__(*args, **kwargs)

    def run_suite(self, suite, **kwargs):
        runner = self.test_runner(
            verbosity=self.verbosity,
            failfast=self.failfast,
        )
        runner.resultclass = runner.resultclass
        result = runner.run(suite)

        if self.show_messages:
            runner.stream.writeln(messages.random(result.wasSuccessful()))

        return result
