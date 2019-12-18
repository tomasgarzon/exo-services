import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.core import signing

from model_utils.models import TimeStampedModel
from utils.email_utils import toHex

from ..manager import UserManager
from ..signals_define import (signal_password_updated,
                              signal_exo_user_request_new_password)
from ..conf import settings


class User(
        AbstractBaseUser,
        PermissionsMixin,
        TimeStampedModel):

    id = models.UUIDField(primary_key=True, default=None, editable=False)
    password_updated = models.BooleanField(default=False)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True
    )
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        permissions = settings.EXO_AUTH_ALL_PERMISSIONS

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.is_superuser

    @property
    def can_authenticate(self):
        """
        A user can authenticate when is active and has a usable password
        """
        return self.is_active and self.has_usable_password()

    @property
    def username(self):
        return getattr(self, self.USERNAME_FIELD)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.pk = uuid.uuid4()
        super().save(*args, **kwargs)

    def set_password(self, raw_password, random_password=False):
        super().set_password(raw_password)
        if raw_password:
            self.password_updated = not random_password
            if self.pk:
                self.save(update_fields=['password_updated'])
            signal_password_updated.send_robust(
                sender=User,
                instance=self,
                password=raw_password)

    def set_unusable_password(self):
        # Set a value that will never be a valid hash
        super().set_unusable_password()
        self.password_updated = False
        if self.pk:
            self.save(update_fields=['password_updated'])

    def add_email_address(self, email, verified=False):
        """
            Add a new email address to user
        """
        return self.emailaddress_set.add_email(self, email, verified)

    def send_notification_change_password(self, email_to=None):
        token = signing.dumps(str(self.pk))
        send_to = email_to or self.email
        cipher_email = toHex(send_to)

        signal_exo_user_request_new_password.send(
            sender=self.__class__,
            recipients=[send_to],
            token=token,
            cipher_email=cipher_email,
            name=self.email)
