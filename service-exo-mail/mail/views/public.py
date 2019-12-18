# django imports
from django.core import signing
from django.http import Http404

from ..handlers import mail_handler


def public_view(request, hash):
    values = signing.loads(hash)
    mail_view_name = values.pop('view_name', None)
    if not mail_view_name:
        raise Http404
    view = mail_handler._registry[mail_view_name].__class__.as_view()
    return view(request, **values)
