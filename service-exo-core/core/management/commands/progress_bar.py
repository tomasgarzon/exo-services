import sys

from datetime import datetime


class ProgressBar:

    FILL_CHARACTER = '▒'

    SUFFIX = 'Complete'
    LENGTH = 100

    DECIMALS = 1

    def __init__(self, title, total, *args, **kwargs):
        self._start_time = datetime.now()
        self._total = total
        self._prefix = title
        self._current_step = 0

        self._length = kwargs.get('lenght', self.LENGTH)
        self._fill = kwargs.get('fill', self.FILL_CHARACTER)
        self._suffix = kwargs.get('suffix', self.SUFFIX)
        self._length = kwargs.get('length', self.LENGTH)

        self._decimals = self.DECIMALS

    @property
    def time_elapsed(self):
        return self._total_time

    def step(self, message='', step=1):
        self._current_step += step
        last_step = self._current_step == self._total
        percent = (
            '{0:.' + str(self._decimals) + 'f}').format(
                100 * (self._current_step / float(self._total))
        )
        filledLength = int(self._length * self._current_step // self._total)
        bar = self._fill * filledLength + '-' * (self._length - filledLength)
        sys.stdout.write('\n')
        sys.stdout.write('\033[F')
        sys.stdout.write('\x1b[2K')
        sys.stdout.write('\r%s %s %s%% %s %s of %s %s' % (
            self._prefix,
            bar,
            percent,
            self._suffix,
            self._current_step,
            self._total,
            '» {}'.format(message) if message and not last_step else ''
        ))

        if last_step:
            self._total_seconds = (datetime.now() - self._start_time).seconds
            sys.stdout.write('  Done in {}min! \n\n'.format(
                round(self._total_seconds, 2) / 60
            ))
