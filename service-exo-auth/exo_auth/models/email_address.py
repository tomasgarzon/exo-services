import hashlib
from random import random

from django.contrib import messages
from django.db import models
from django.utils import timezone

from model_utils.models import TimeStampedModel

from utils.email_utils import build_context_dict, get_site

from ..conf import settings
from ..exceptions import (InactiveAccountException,
                          AlreadyVerifiedException,
                          InvalidKeyException)
from ..manager import EmailAddessManager
from ..signals_define import signal_exo_user_new_email_address_unverified
from ..settings import MM


class EmailAddress(TimeStampedModel):
    """An e-mail address for a Django User. Users may have more than one
    e-mail address. The address that is on the user object itself as the
    email property is considered to be the primary address, for which there
    should also be an EmailAddress object associated with the user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.deletion.CASCADE)
    email = models.EmailField(max_length=100, unique=True)
    verif_key = models.CharField(max_length=40)
    verified_at = models.DateTimeField(default=None, null=True, blank=True)
    remote_addr = models.GenericIPAddressField(null=True, blank=True)
    remote_host = models.CharField(max_length=255, null=True, blank=True)
    is_primary = models.BooleanField(default=False)

    objects = EmailAddessManager()

    def __str__(self):
        return '{} <{}> - Primary: {} - Verified: {}'.format(
            self.user,
            self.email,
            self.is_primary,
            self.is_verified)

    @property
    def created_at(self):
        return self.created

    @property
    def is_verified(self):
        """Is this e-mail address verified? Verification is indicated by
        existence of a verified_at timestamp which is the time the user
        followed the e-mail verification link."""
        return bool(self.verified_at)

    def set_verified(self):
        self.verified_at = timezone.now()
        self.save(update_fields=['verified_at'])

    def _set_primary_flags(self):
        """Set this email's is_primary to True and all others for this
        user to False."""
        for email in self.user.emailaddress_set.all():
            if email == self:
                if not email.is_primary:
                    email.is_primary = True
                    email.save(update_fields=['is_primary'])
            else:
                if email.is_primary:
                    email.is_primary = False
                    email.save(update_fields=['is_primary'])

    def set_primary(self):
        """Set this e-mail address to the primary address by setting the
        email property on the user."""
        self.user.email = self.email
        self.user.save(update_fields=['email'])
        self._set_primary_flags()

    def save(self, verify=True, request=None, *args, **kwargs):
        """Save this EmailAddress object."""
        if not self.verif_key:
            salt = hashlib.sha1(str(random()).encode('ascii')).hexdigest()[:5]
            self.verif_key = hashlib.sha1((salt + self.email).encode('utf8')).hexdigest()
        if verify and not self.pk:
            verify = True
        else:
            verify = False
        super(EmailAddress, self).save(*args, **kwargs)
        if verify:
            self.send_verification(request=request)

    def delete(self):
        """Delete this EmailAddress object."""
        user = self.user
        super(EmailAddress, self).delete()
        addrs = user.emailaddress_set.filter(verified_at__isnull=False)
        if addrs:
            addrs[0].set_primary()
        else:
            if MM.DELETE_PRIMARY:
                user.email = ''
                user.save()

    def send_verification(self, request=None):
        """Send email verification link for this EmailAddress object.
        Raises smtplib.SMTPException, and NoRouteToHost.
        """
        site = get_site(request)
        d = build_context_dict(site, self)
        signal_exo_user_new_email_address_unverified.send(
            sender=self.__class__,
            recipients=[self.email],
            user_name=d.get('email'),
            verify_link=d.get('verify_link'))

        if MM.USE_MESSAGES:
            message = MM.VERIFICATION_LINK_SENT_MESSAGE % d
            if request is not None:
                messages.success(request, message,
                                 fail_silently=not MM.USE_MESSAGES)
            else:
                try:
                    self.user.message_set.create(message=message)
                except AttributeError:
                    pass

    def verify_discard(self, verif_key, raise_exception=True):
        """
        Check if the email can be discarted
        """
        verified = False
        message = None

        try:
            if not self.verif_key == verif_key:
                raise InvalidKeyException

            if self.is_verified:
                raise AlreadyVerifiedException

            if not MM.ALLOW_VERIFICATION_OF_INACTIVE_ACCOUNTS and \
                    not self.user.is_active:
                raise InactiveAccountException

            verified = True

        except InvalidKeyException:
            if raise_exception:
                raise

            message = MM.INVALID_VERIFICATION_LINK_MESSAGE

        except InactiveAccountException:
            if raise_exception:
                raise
            message = MM.INACTIVE_ACCOUNT_MESSAGE

        except AlreadyVerifiedException:
            """Only allow a single verification to prevent abuses, such as
            re-verifying on a deactivated account."""
            if raise_exception:
                raise
            message = MM.EMAIL_ALREADY_VERIFIED_MESSAGE

        return verified, message

    def verify_resend_link(self, verif_key, raise_exception=True):

        verified = False
        message = None

        try:
            if self.is_verified:
                raise AlreadyVerifiedException

            if not MM.ALLOW_VERIFICATION_OF_INACTIVE_ACCOUNTS and \
                    not self.user.is_active:
                raise InactiveAccountException

            verified = True

        except InactiveAccountException:
            if raise_exception:
                raise

            message = MM.INACTIVE_ACCOUNT_MESSAGE

        except AlreadyVerifiedException:
            """Only allow a single verification to prevent abuses, such as
            re-verifying on a deactivated account."""
            if raise_exception:
                raise

            message = MM.EMAIL_ALREADY_VERIFIED_MESSAGE

        return verified, message
