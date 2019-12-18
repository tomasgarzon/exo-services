import re


def split_filename(file_name):
    exp = '(.*?)(\.[^.]*$|$)'
    regex = re.compile(exp)
    result = regex.match(file_name)
    return result.groups()
