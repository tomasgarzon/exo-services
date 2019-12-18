import string

from random import Random

random = Random()


def build_hash(n=40):
    return ''.join(
        random.choice(
            string.ascii_letters + string.digits,
        ) for _ in range(n)
    )
