from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import OuterRef, Exists

from core.models import Language
from registration.models import RegistrationProcess
from achievement.models import Achievement
from account_config.models import ConfigParam

from ..querysets.consultant import ConsultantQuerySet
from ..helpers.groups import group_waiting_list


class ConsultantManager(models.Manager):

    def get_queryset(self):
        return ConsultantQuerySet(self.model, using=self._db).filter(
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )

    def filter_complex(self, *args, **kwargs):
        return self.get_queryset().filter_complex(*args, **kwargs)

    def filter_by_user_permissions(self, *args, **kwargs):
        return self.get_queryset().filter_by_permission_codename(*args, **kwargs)

    def only_showing_web(self, type_site):
        return self.get_queryset().filter_showing_web(type_site)

    def filter_can_receive_new_opportunities(self):
        perms = [settings.EXO_ACCOUNTS_PERMS_MARKETPLACE_FULL]
        queryset = self.get_queryset().filter_by_permission_codename(perms)

        config_params = ConfigParam.objects.filter(
            user=OuterRef('user_id'),
            name='new_open_opportunity',
            values___value=False)

        return queryset.annotate(
            activate=Exists(config_params)).filter(activate=False)

    def filter_can_receive_new_tickets(self):
        perms = [settings.EXO_ACCOUNTS_PERMS_MARKETPLACE_FULL]
        queryset = self.get_queryset().filter_by_permission_codename(perms)

        config_params = ConfigParam.objects.filter(
            user=OuterRef('user_id'),
            name='new_open_ticket',
            values___value=False)

        return queryset.annotate(
            activate=Exists(config_params)).filter(activate=False)

    def filter_by_config_param(self, config_param):

        config_params = ConfigParam.objects.filter(
            user=OuterRef('user_id'),
            name=config_param,
            values___value=False)

        return self.get_queryset().annotate(
            activate=Exists(config_params)).filter(activate=False)

    def filter_consulting_enabled(self):
        return self.get_queryset().filter_consulting_enabled()

    def activate_existing_user(cls, user, created):
        if not created and not user.is_active:
            user.activate(user_from=user)

    def initialize_created_user(cls, user, **kwargs):
        for (key, value) in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        user.save()

    def initialize_languages(cls, consultant, user_languages):
        [
            consultant.languages.add(Language.objects.get(name=lang))
            for lang in user_languages
        ]

    def create_consultant(
        cls, short_name, email,
        invite_user=None, registration_process=False,
        *args, **kwargs
    ):
        user, created = get_user_model().objects.get_or_create(
            email=email,
            defaults={'short_name': short_name},
            user_from=invite_user,
        )

        cls.activate_existing_user(user, created)

        if created:
            cls.initialize_created_user(user, **kwargs)

        consultant = cls.model(
            user=user)
        consultant.save()

        Achievement.objects.create_reward_for_consultant(consultant, kwargs.get('coins', None))

        if kwargs.get('waiting_list', False):
            user.groups.add(group_waiting_list())

        cls.initialize_languages(
            consultant,
            kwargs.pop('languages', settings.CONSULTANT_DEFAULT_LANGUAGES),
        )

        if registration_process:
            RegistrationProcess.create_process(
                user_from=invite_user or user,
                user=consultant.user,
                custom_text=kwargs.get('custom_text', None),
                skip_steps=kwargs.get('skip_steps', []),
                version=kwargs.get('version', None),
                entry_point=kwargs.get('entry_point', None),
            )

        if kwargs.get('password') is not None:
            user = consultant.user
            user.set_password(kwargs.get('password'))
            user.save()

        return consultant


class AllConsultantManager(ConsultantManager):

    def get_queryset(self):
        return ConsultantQuerySet(self.model, using=self._db)
