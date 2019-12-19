# -*- coding: utf-8 -*-
"""
License boilerplate should be used here.
"""
# python imports
import re

_underscorer1 = re.compile(r'(.)([A-Z][a-z]+)')
_underscorer2 = re.compile('([a-z0-9])([A-Z])')


def pairwise(iterable):
    """
    's -> (s0, s1), (s2, s3), (s4, s5), ...'
    """
    a = iter(iterable)
    return zip(a, a)


def camel_to_snake(s):
    """
    Convert a CamelCase text to snake_case name
    https://gist.github.com/jaytaylor/3660565
    """
    subbed = _underscorer1.sub(r'\1_\2', s)
    return _underscorer2.sub(r'\1_\2', subbed).lower()


# Method to transform string to hex
def toHex(x):
    return ''.join([hex(ord(c))[2:].zfill(2) for c in x])


def hexToString(x):
    return ''.join([chr(int('{}{}'.format(x, y), 16)) for x, y in pairwise(x)])
