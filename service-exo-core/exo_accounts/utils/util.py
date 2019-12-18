from django.urls import reverse
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured

from ..settings import MM


def build_context_dict(site, emailobj):
    user = emailobj.user
    d = {
        'current_site_domain': site.domain,
        'current_site_id': site.pk,
        'current_site_name': site.name,
        'emailaddress_id': emailobj.pk,
        'email': emailobj.email,
        'short_name': user.short_name,
        'full_name': user.full_name,
        'primary_email': user.email,
        'user_id': user.pk,
        'username': user.username,
        'verif_key': emailobj.verif_key
    }

    try:
        veriry_url = MM.EMAIL_VERIFICATION_URL_VIEW_NAME
        assert(veriry_url)
    except AssertionError:
        raise ImproperlyConfigured(
            'Please define a valid url at EXO_ACCOUNTS_EMAIL_VERIFIACTION_URL, to verify new Email')

    verify_link = reverse(veriry_url,
                          kwargs={'email_pk': d.get('emailaddress_id'),
                                  'verif_key': d.get('verif_key')})

    d['verify_link'] = verify_link

    return d


def get_site(request=None):
    """Return Site object according to Multimail configuration preferences.
    SITE_DOMAIN / SITE_NAME if they are both set in the Multimail settings.
    Otherwise, try the current sites configuration (using the request object
    if it is available) and finally fall back to example.com / Example rather
    than throwing an exception for wrong configurations."""
    if getattr(MM, 'SITE_DOMAIN') is not None and \
            getattr(MM, 'SITE_NAME') is not None:
        site = Site(domain=MM.SITE_DOMAIN, name=MM.SITE_NAME, pk=0)
    else:
        try:
            if request is not None:
                site = get_current_site(request)
            else:
                site = Site.objects.get_current()
        except (ImproperlyConfigured, Site.DoesNotExist):
            domain = 'example.com'
            name = 'Example'
            site = Site(domain=domain, name=name, pk=0)
    return site


def normalize_email(email):
    """
    Normalize the email address by lowercasing the domain/email name part of it.
    """
    email = email or ''
    try:
        email_name, domain_part = email.strip().rsplit('@', 1)
    except ValueError:
        pass
    else:
        email = '@'.join([email_name.lower(), domain_part.lower()])
    return email
