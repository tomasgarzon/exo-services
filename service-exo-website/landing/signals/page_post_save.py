from ..populate import populate
from .. import process


def save_page_handler(sender, instance, **kwargs):
    created = kwargs.get('created')
    if created and not kwargs.get('raw'):
        populate(instance)


def update_website_handler(sender, instance, **kwargs):
    process.build(instance)
