from django.apps import apps
from django.core.mail import mail_admins
from django.utils import timezone

from ..settings import MM


def email_address_handler(sender, **kwargs):  # NOQA
    """Ensures that there is a multimail version of the email address on the
    django user object and that email is set to primary."""
    EmailAddress = apps.get_model('exo_accounts', 'EmailAddress')

    user = kwargs['instance']
    if not user.email:
        return
    if kwargs.get('raw', False):
        # don't create email entry when loading fixtures etc.
        return
    try:
        if MM.SEND_EMAIL_ON_USER_SAVE_SIGNAL:
            if user.email:
                addr = EmailAddress.objects.filter(
                    user=user,
                    email__iexact=user.email)
                if addr:
                    addr = addr[0]
                else:
                    addr = EmailAddress(user=user, email=user.email)
                    addr.verified_at = timezone.now()
                    addr.save(verify=False)
        else:
            try:
                addr = EmailAddress.objects.get(user=user, email=user.email)
                # Provides that an address that has been just verified
                # without use of django-multimail, is still considered
                # verified in conditions of django-multimail
                if MM.AUTOVERIFY_ACTIVE_ACCOUNTS and \
                   user.is_active and not addr.verified_at:
                    addr.verified_at = timezone.now()
            except EmailAddress.DoesNotExist:
                addr = EmailAddress()
                addr.user = user
                addr.email = user.email
            addr.save(verify=False)
        addr._set_primary_flags()  # do this for every save in case things
        # get out of sync
    except Exception as e:
        msg = """An attempt to create EmailAddress object for user {}, email
{} has failed. This may indicate that an EmailAddress object for that email
already exists in the database. This situation can occur if, for example, a
user is manually created through the admin panel or the shell with an email
address that is the same as an existing EmailAddress objects. \n\n{} """.format(
            user.get_full_name(), user.email, e)
        subj = 'Failed attempt to create Multimail email address.'
        if MM.EMAIL_ADMINS:
            mail_admins(subj, msg)
