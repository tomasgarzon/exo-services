""" Markdown utils. """
import markdown as markdown_module

from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.conf import settings

MARKDOWN_EXTENSIONS = getattr(settings, 'MARKDOWN_EXTENSIONS', [])
MARKDOWN_EXTENSION_CONFIGS = getattr(settings, 'MARKDOWN_EXTENSION_CONFIGS', {})


def markdown(value, extensions=MARKDOWN_EXTENSIONS,
             extension_configs=MARKDOWN_EXTENSION_CONFIGS,
             safe=False):
    """ Render markdown over a given value, optionally using varios extensions.
    Default extensions could be defined which MARKDOWN_EXTENSIONS option.
    :returns: A rendered markdown
    """
    return mark_safe(markdown_module.markdown(
        force_text(value), extensions=extensions,
        extension_configs=extension_configs, safe_mode=safe))
