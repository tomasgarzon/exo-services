from django.conf import settings
from django.db import models
from django.utils import timezone

from utils.email_utils import normalize_email


class EmailAddessManager(models.Manager):
    use_for_related_fields = True

    @classmethod
    def normalize_email(cls, email):
        return normalize_email(email)

    def add_email(self, user, email, verified=False):
        email_address = self.model(
            user=user, email=self.normalize_email(email))
        if verified:
            email_address.verified_at = timezone.now()
        email_address.save(verify=not verified)
        return email_address

    def check_email_exist_and_verified(self, user, email, email_address=None):
        status = False
        code = settings.EXO_AUTH_VALIDATION_CHOICES_NOT_OWNER

        if not email_address:
            emails = self.get_queryset().filter(user=user, email=email)
            if emails.exists():
                email_address = emails.get()

        if email_address:
            if email_address.is_verified:
                status = True
                code = settings.EXO_AUTH_VALIDATION_CHOICES_VERIFIED
            else:
                status = False
                code = settings.EXO_AUTH_VALIDATION_CHOICES_NOT_VERIFIED

        return status, code

    def check_email(self, user, email):
        status = True
        code = ''

        if not user.email == email:
            emails = self.get_queryset().filter(user=user, email=email)
            if emails.exists():
                email_address = emails.get()
                status, code = self.check_email_exist_and_verified(
                    user=None,
                    email=None,
                    email_address=email_address)

            elif self.get_queryset().filter(email=email).exists():
                status = False
                code = settings.EXO_AUTH_VALIDATION_CHOICES_OTHER_USER

            else:
                status = True
                code = settings.EXO_AUTH_VALIDATION_CHOICES_PENDING

        return status, code

    def change_user_email(self, user_from, user, email):
        email = self.normalize_email(email)
        if user.email == email:
            return True, ''
        status, code = self.check_email(user, email)
        if status:
            if code == settings.EXO_AUTH_VALIDATION_CHOICES_VERIFIED:
                user.email = email
                user.save()
            else:
                if user_from == user:
                    # the same user has to validate the email
                    user.add_email_address(email)
                else:
                    # user_from is admin, so the user doesn't need to validate
                    user.email = email
                    user.save()
                    return True, ''
        else:
            # email pending of validation
            email = self.get_queryset().get(user=user, email=email)
            if user_from == user:
                email.send_verification()
            else:
                email.set_verified()
                email.set_primary()
                return True, ''
        return status, code

    def add_user_email(self, user, email):
        """
        Add an email to this user, verified.
        This method has to check if this email is available and check if it's unverified
        Action:
        - Create a new EmailAddress verified if email is available (free). Return True
        - Verify EmailAddress if this email is associated with this user previously. Return True
        - Return False, when this email is already used for another user"""
        # Email doesn't exist
        if not self.get_queryset().filter(email=email).exists():
            user.add_email_address(email, verified=True)
        # Email account associated to this user
        elif self.get_queryset().filter(email=email, user=user).exists():
            self.get_queryset().filter(
                email=email,
                user=user).update(verified_at=timezone.now())
        # Email account is being used for another
        else:
            return False
        return True

    def exo_account(self):
        try:
            return self.get_queryset().filter(
                type_email=settings.EXO_AUTH_CH_EXO_EMAIL)[0]
        except IndexError:
            return None
