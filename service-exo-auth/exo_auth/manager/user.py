import logging
import requests

from django.contrib.auth.models import BaseUserManager
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from ..signals_define import signal_exo_accounts_user_created
from ..querysets import UserQuerySet

from utils.email_utils import normalize_email
from utils.uuid_utils import validate_uuid4

logger = logging.getLogger('user')


class UserManager(BaseUserManager):
    use_in_migrations = True
    queryset_class = UserQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model,
                                   using=self._db)

    def get_by_email(self, email):
        return self.get_queryset().get_by_email(email)

    @classmethod
    def normalize_email(cls, email):
        return normalize_email(email)

    def create(self, *args, **kwargs):
        if not kwargs.get('email'):
            raise ValueError('Users must have an email address')
        kwargs['email'] = self.normalize_email(kwargs.get('email'))
        user = self.model(**kwargs)
        if kwargs.get('password'):
            user.set_password(kwargs.get('password'))
        else:
            user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, *args, **kwargs):

        if not kwargs.get('is_active'):
            kwargs['is_active'] = True
        if not kwargs.get('is_superuser'):
            kwargs['is_superuser'] = True

        user = self.create(**kwargs)
        return user

    def active_users(self):
        return self.filter(is_active=True)

    def inactive_users(self):
        return self.filter(is_active=False)

    def admin_users(self):
        return self.filter(is_superuser=True)

    def get_or_create(self, email, defaults={}, *args, **kwargs):
        user = None
        created = False

        user_from = kwargs.get('user_from', None)
        send_notification = kwargs.get('send_notification', False)
        autosend = kwargs.get('autosend', True)
        password = defaults.pop('password', None)

        email = self.normalize_email(email)
        email_addresses = self.filter(emailaddress__email=email)
        if email_addresses.exists():
            user = email_addresses.get()
        else:
            if 'id' in defaults:
                uuid = defaults.pop('id')
                defaults['email'] = email
                user, created = super().get_or_create(
                    id=uuid, defaults=defaults)
            else:
                user, created = super().get_or_create(
                    email=email, defaults=defaults)

        if created:
            signal_exo_accounts_user_created.send(
                sender=user.__class__,
                instance=user,
                from_user=user_from,
                user=user,
                send_notification=send_notification,
                autosend=autosend,
                status=kwargs.get('invitation_status', None))

            if password:
                user.set_password(password)
            else:
                user.set_unusable_password()
            user.save()

        return user, created

    def get_by_natural_key(self, username):
        if validate_uuid4(username):
            USERNAME_FIELD = 'id'
        else:
            USERNAME_FIELD = 'email'
        try:
            user = self.get(**{USERNAME_FIELD: username})
        except self.model.DoesNotExist:
            if USERNAME_FIELD == 'email':
                raise self.model.DoesNotExist
            user = self._retrieve_remote_user_by_uuid(username)
        return user

    def _retrieve_remote_user_by_uuid(self, uuid, retrieve_response=False):
        user = AnonymousUser()
        response = self._retrieve_remote_user_data_by_uuid(uuid)

        if response is not None:
            user, _ = self.update_or_create(
                id=response.get('uuid'),
                email=response.get('email'),
                defaults={
                    'is_active': response.get('isActive', response.get('is_active')),
                    'is_superuser': response.get('isSuperuser', response.get('is_superuser')),
                    'is_staff': response.get('isStaff', response.get('is_staff')),
                }
            )

        if retrieve_response:
            return user, response
        else:
            return user

    def _retrieve_remote_user_data_by_uuid(self, uuid):
        url = settings.URL_VALIDATE_USER_UUID.format(uuid)
        response = None
        try:
            response = requests.get(
                url,
                headers={'USERNAME': settings.AUTH_SECRET_KEY})
        except Exception:
            response = None

        if response and response.status_code == requests.codes.ok:
            return response.json()
        return None
