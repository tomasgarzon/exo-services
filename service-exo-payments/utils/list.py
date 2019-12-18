from operator import is_not
from functools import partial


def remove_element(list_origin, element):
    return list(filter(partial(is_not, element), list_origin))
