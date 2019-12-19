import collections
from functools import total_ordering


@total_ordering
class StatusString(collections.UserString):
    _choices = []

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        super().__init__(*args, **kwargs)
        self.clean_choices(choices)

    def clean_choices(self, choices):
        if type(choices) == list:
            self._choices = choices
        elif type(choices) == tuple:
            self._choices = list(collections.OrderedDict(choices))
        else:
            raise AttributeError('choices parameter has to be list or tuple')

    def _index(self, other):
        p1 = self._choices.index(str(self))
        p2 = self._choices.index(other)
        return p1, p2

    def __ge__(self, other):
        current_value, other_value = self._index(other)
        return current_value >= other_value

    def __eq__(self, other):
        current_value, other_value = self._index(other)
        return current_value == other_value

    def __gt__(self, other):
        current_value, other_value = self._index(other)
        return current_value > other_value
