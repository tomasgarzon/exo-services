from django import template

from utils.markdown import markdown as _markdown
from utils.markdown import MARKDOWN_EXTENSIONS


register = template.Library()


@register.filter(is_safe=True)
def markdown_safe(value, arg=None):
    """ Render markdown over a given value, optionally using varios extensions.
    Default extensions could be defined which MARKDOWN_EXTENSIONS option.
    Enables safe mode, which strips raw HTML and only returns HTML generated
    by markdown.
    :returns: A rendered markdown.
    """
    extensions = (arg and arg.split(',')) or MARKDOWN_EXTENSIONS
    return _markdown(value, extensions=extensions, safe=True)
