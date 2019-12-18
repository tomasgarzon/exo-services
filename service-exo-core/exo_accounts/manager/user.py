import logging

from django.contrib.auth.models import BaseUserManager

from ..signals_define import signal_exo_accounts_user_created
from ..utils.util import normalize_email
from ..querysets import UserQuerySet
from ..helper import validate_uuid4

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

    @classmethod
    def merge_empty_user(cls, user, user_to_merge):
        """
        Merge the user_to_merge user into the user param:
            - user: user to merge in
            - user_to_merge: user to delete
            - Move Survey to actual user
            - Remove user_to_merge
        """
        merge_done = False
        if user_to_merge.is_empty_user():
            merge_done = True
            for user_related_class in user_to_merge.get_user_empty_classes():
                if callable(getattr(user_related_class.objects, 'merge_users', None)):
                    merged_data = user_related_class.objects.merge_users(user, user_to_merge)

                    logger.info('Meged empty user {} into {} - Updated {}: {}'.format(
                        user_to_merge.email,
                        user.email,
                        user_related_class.__name__,
                        merged_data))

            objects_deleted = user_to_merge.delete()
            logger.info('Deleted merged user: {}'.format(objects_deleted))

        return merge_done

    def create_user(self, *args, **kwargs):
        if not kwargs.get('email'):
            raise ValueError('Users must have an email address')

        kwargs['email'] = self.normalize_email(kwargs.get('email'))
        user = self.model(**kwargs)
        if kwargs.get('password'):
            user.set_password(kwargs.get('password'))
        else:
            new_password = self.make_random_password()
            user.set_password(new_password, random_password=True)
        user.save(using=self._db)
        return user

    def create_superuser(self, *args, **kwargs):

        if not kwargs.get('is_active'):
            kwargs['is_active'] = True
        if not kwargs.get('is_superuser'):
            kwargs['is_superuser'] = True

        user = self.create_user(**kwargs)
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

        user_from = kwargs.pop('user_from', None)
        send_notification = kwargs.get('send_notification', False)
        autosend = kwargs.get('autosend', True)
        password = defaults.pop('password', None)

        email = self.normalize_email(email)
        email_addresses = self.filter(emailaddress__email=email)

        if email_addresses.exists():
            user = email_addresses.get()
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
                new_password = self.make_random_password()
                user.set_password(new_password, random_password=True)
            user.save()
        return user, created

    def consultants(self):
        return self.get_queryset().filter(consultant__isnull=False)

    def get_platform_languages(self, users_email):
        return self.get_queryset().get_platform_languages(users_email)

    def get_by_natural_key(self, username):
        valid_uuid = validate_uuid4(username)
        if valid_uuid:
            return self.get(**{self.model.ALTERNATIVE_USERNAME_FIELD: username})
        else:
            return self.get(**{self.model.USERNAME_FIELD: username})
