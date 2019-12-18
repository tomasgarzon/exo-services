import time
import unittest

from rainbowtests.test.core import RainbowTextTestResult
from rainbowtests.colors import magenta, red, green, yellow


SHOW_SLOW_TEST = False
DEFAULT_TEST_THRESHOLD = 2.0


class TimeLoggingTestResult(RainbowTextTestResult):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_timings = []
        self.clocks = dict()

    def startTest(self, test):
        self.clocks[test] = time.time()
        super().startTest(test)

    def addSuccess(self, test):
        super().addSuccess(test)
        elapsed = self.get_elapsed(test)
        name = self.getDescription(test)
        test_threshold = 0

        try:
            test_threshold = getattr(test, 'TEST_THRESHOLD')
        except AttributeError:
            pass

        self.test_timings.append((name, elapsed, test_threshold))
        self.print_description_line(test)
        self.print_success_line(test)
        self.stream.flush()

    def addError(self, test, err):
        super().addError(test, err)
        self.print_description_line(test)
        self.print_error_line(test)
        self.stream.flush()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.print_description_line(test)
        self.print_failure_line(test)
        self.stream.flush()

    def getTestTimings(self):
        return self.test_timings

    def get_elapsed(self, test):
        try:
            return time.time() - self.clocks[test]
        except KeyError:
            pass

    def print_description_line(self, test):
        self.stream.write(self.getDescription(test))
        self.stream.write(' ... ')

    def print_success_line(self, test):
        line = green('ok-dokey ') + self.get_elapsed_line(test)
        self.stream.writeln(line)

    def print_error_line(self, test):
        line = red('error ') + self.get_elapsed_line(test)
        self.stream.writeln(line)

    def print_failure_line(self, test):
        line = red('failure ') + self.get_elapsed_line(test)
        self.stream.writeln(line)

    def get_elapsed_line(self, test):
        elapsed = self.get_elapsed(test)
        if elapsed is None:
            return ''
        if elapsed > (DEFAULT_TEST_THRESHOLD or self.slow_test_threshold):
            line = yellow('(%.6fs)' % (elapsed))
        else:
            line = magenta('(%.6fs)' % (elapsed))
        return line


class TimeLoggingTestRunner(unittest.TextTestRunner):

    resultclass = TimeLoggingTestResult

    def __init__(self, slow_test_threshold=DEFAULT_TEST_THRESHOLD, *args, **kwargs):
        self.slow_test_threshold = slow_test_threshold
        super().__init__(
            resultclass=TimeLoggingTestResult,
            *args,
            **kwargs
        )

    def run(self, test):
        result = super().run(test)

        if SHOW_SLOW_TEST:
            line = '\nSlow Tests (>{:.03}s) [Default]:'.format(self.slow_test_threshold)
            self.stream.writeln(line)
            self.print_slow_tests(result)
        return result

    def print_slow_tests(self, result):
        for name, elapsed, threshold in result.getTestTimings():
            if elapsed > (threshold or self.slow_test_threshold):
                self.stream.writeln(
                    yellow(
                        '[takes ({:.03}s) margin: {}] - {}'.format(
                            elapsed,
                            threshold or self.slow_test_threshold,
                            name,
                        ),
                    ),
                )
