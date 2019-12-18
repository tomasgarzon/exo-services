from random import Random
import string
import itertools as _itertools
import bisect as _bisect


def monkeypatch_method(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator


@monkeypatch_method(Random)
def choices(self, population, weights=None, *, cum_weights=None, k=1):
    """Return a k sized list of population elements chosen with replacement.
    If the relative weights or cumulative weights are not specified,
    the selections are made with equal probability.
    """
    random = self.random
    if cum_weights is None:
        if weights is None:
            _int = int
            total = len(population)
            return [population[_int(random() * total)] for i in range(k)]
        cum_weights = list(_itertools.accumulate(weights))
    elif weights is not None:
        raise TypeError('Cannot specify both weights and cumulative weights')
    if len(cum_weights) != len(population):
        raise ValueError('The number of weights does not match the population')
    bisect = _bisect.bisect
    total = cum_weights[-1]
    return [population[bisect(cum_weights, random() * total)] for i in range(k)]


random = Random()


def build_name(n=20):
    filename = ''.join(
        random.choice(
            string.ascii_letters + string.digits,
        ) for _ in range(n)
    )
    return filename


def weightedChoice(choices):
    """Like random.choice, but each element can have a different chance of being selected.
    choices can be any iterable containing iterables with two items each.
    The first item is the thing being chosen, the second item is
    its weight.  The weights can be any numeric values, what matters is the relative differences between them.
    """
    space = {}
    current = 0
    for choice, weight in choices:
        if weight > 0:
            space[current] = choice
            current += weight
    rand = random.uniform(0, current)
    for key in sorted(list(space.keys()) + [current]):
        if rand < key:
            return choice
        choice = space[key]
    return None
