from django.db import models
from django.apps import apps

from invitation.models import Invitation

from ..conf import settings
from ..querysets.consultant_validation_status import ConsultantValidationStatusQuerySet


class ConsultantValidationStatusManager(models.Manager):
    use_for_related_fields = True
    queryset_class = ConsultantValidationStatusQuerySet

    def get_queryset(self):
        return self.queryset_class(
            self.model,
            using=self._db,
        )

    def create(self, **kwargs):
        """
            Some extra params:
                - autosend
        """
        # Clean exta kwargs for super create method
        autosend = kwargs.pop('autosend', None)
        created = False
        try:
            consultant_validation_status = self.get(
                validation=kwargs.get('validation'),
                consultant=kwargs.get('consultant'),
            )
        except self.model.DoesNotExist:
            created = True
            consultant_validation_status = super().create(**kwargs)

        if created:
            invitation = Invitation.objects.create_consultant_validation_invitation(
                user_from=consultant_validation_status.user_from,
                user_to=consultant_validation_status.consultant.user,
                validation_obj=consultant_validation_status,
                autosend=autosend,
            )
            consultant_validation_status.generate_related_object(invitation)
        else:
            invitation = Invitation.objects.filter_by_object(consultant_validation_status).get()
            invitation.reactivate(kwargs.get('user_from'), autosend=autosend)
        consultant_validation_status.refresh_from_db()
        return consultant_validation_status

    def create_validation(
        self, user_from, validation, custom_text=None,
        *args, **kwargs
    ):
        validation_status = self.create(
            validation=validation,
            user_from=user_from,
            _description=custom_text,
            *args, **kwargs
        )

        return validation_status

    def create_validation_by_name(
        self, user_from, validation_name,
        custom_text=None, *args, **kwargs
    ):
        ConsultantValidation = apps.get_model(
            'consultant',
            'ConsultantValidation',
        )
        try:
            validation = ConsultantValidation.objects.get(name=validation_name)
        except ConsultantValidation.DoesNotExist as e:
            if validation_name in [_[0] for _ in settings.CONSULTANT_VALIDATION_CH_TYPE]:
                validation = ConsultantValidation(name=validation_name)
                validation.save()
            else:
                raise e

        return self.create_validation(
            user_from=user_from,
            validation=validation,
            custom_text=custom_text,
            *args, **kwargs
        )

    def agreements(self):
        return self.get_queryset().filter_agreements()

    def skillassessments(self):
        raise Exception('Not supported')

    def applications(self):
        return self.get_queryset().filter_application()

    def tests(self):
        return self.get_queryset().filter_test()

    def denied(self):
        return self.get_queryset().filter_denied()

    def accepted(self):
        return self.get_queryset().filter_accepted()

    def waiting(self):
        return self.get_queryset().filter_waiting()
