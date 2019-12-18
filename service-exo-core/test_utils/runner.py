import time

from django_nose import NoseTestSuiteRunner

from .test_runner_mixin import TestRunnerMixin, RunnerSetupMixin
from .runner_slow_test import SlowTestRunner


class TestRunner(TestRunnerMixin, SlowTestRunner):

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        initial = time.time()
        self.setup_test_environment()
        setup_time = time.time()
        suite = self.build_suite(test_labels, extra_tests)
        suite_time = time.time()
        old_config = self.setup_databases()
        database_time = time.time()
        self.run_checks()
        check_time = time.time()
        result = self.run_suite(suite)
        result_time = time.time()
        self.teardown_databases(old_config)
        self.teardown_test_environment()
        teardown_time = time.time()

        print('Setup test environment (%.6fs)' % (setup_time - initial))    # noqa
        print('Build Suite (%.6fs)' % (suite_time - setup_time))    # noqa
        print('Setup databases (%.6fs)' % (database_time - suite_time))    # noqa
        print('Run checks (%.6fs)' % (check_time - database_time))    # noqa
        print('Run suite (%.6fs)' % (result_time - check_time))    # noqa
        print('Teardown test environment (%.6fs)' % (teardown_time - result_time))    # noqa
        return self.suite_result(suite, result)


class CoverageTestRunner(RunnerSetupMixin, NoseTestSuiteRunner):
    pass
