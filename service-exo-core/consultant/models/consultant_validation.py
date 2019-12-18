from django.db import models

from model_utils.models import TimeStampedModel

from utils.mail import handlers

from ..conf import settings


class ConsultantValidation(TimeStampedModel):
    """
    Consultant Validation types
    """
    name = models.CharField(
        max_length=1,
        choices=settings.CONSULTANT_VALIDATION_CH_TYPE,
        null=False, blank=False,
    )

    class Meta:
        verbose_name_plural = 'Consultants Validations'
        verbose_name = 'Consultant Validation'

    def __str__(self):
        return str('%s' % self.get_name_display())

    @property
    def mail_view_name(self):
        """
        View name to use with the Mail application
        """
        return 'consultant_validation_%s' % self.get_name_display().lower().replace(' ', '_')

    @property
    def is_user(self):
        return self.name == settings.CONSULTANT_VALIDATION_USER

    @property
    def is_skill_assessment(self):
        return self.name == settings.CONSULTANT_VALIDATION_SKILL_ASSESSMENT

    @property
    def is_agreement(self):
        return self.name == settings.CONSULTANT_VALIDATION_AGREEMENT

    @property
    def is_profile(self):
        return self.name == settings.CONSULTANT_VALIDATION_BASIC_PROFILE

    def is_application(self):
        return self.name == settings.CONSULTANT_VALIDATION_APPLICATION

    @property
    def is_test(self):
        return self.name == settings.CONSULTANT_VALIDATION_TEST

    @property
    def frontend_name(self):
        return settings.CONSULTANT_VALIDATION_FRONTEND_CH_TYPE.get(
            self.name,
        )

    def get_public_url(
        self, invitation,
        *args, **kwargs
    ):
        if self.is_agreement:
            return settings.FRONTEND_REGISTRATION_STEP_PAGE.format(
                **{'hash': invitation.hash, 'section': 'agreement'})
        elif self.is_user:
            return settings.FRONTEND_AUTH_SIGNUP_PAGE.format(
                **{'hash': invitation.hash})
        elif self.is_profile:
            return settings.FRONTEND_REGISTRATION_STEP_PAGE.format(
                **{'hash': invitation.hash, 'section': 'profile'})
        # Not developed yet others cases
        return ''

    def _build_mail_kwargs(self, name, public_url, description):
        return {
            'user_name': name,
            'public_url': public_url,
            'description': description,
        }

    def send_notification(
        self, consultant_validation, invitation,
        *args, **kwargs
    ):
        """
        Finally the notification for this Step validation will be
        sent to the user
        """
        mail_kwargs = self._build_mail_kwargs(
            name=consultant_validation.consultant.get_short_name(),
            public_url=consultant_validation.get_public_url(invitation),
            description=invitation.description,
        )
        mail_kwargs['recipients'] = [consultant_validation.consultant.user.email]
        mail_kwargs['user_in_waiting_list'] = consultant_validation.consultant.is_in_waiting_list
        handlers.mail_handler.send_mail(
            self.mail_view_name,
            **mail_kwargs
        )

        return True

    def preview_notification(self, name, description):

        class Invitation(object):
            def __init__(self, _id):
                self.hash = _id

        invitation = Invitation(0)
        mail_kwargs = self._build_mail_kwargs(
            name=name,
            public_url=self.get_public_url(invitation),
            description=description,
        )
        mail_kwargs['preview'] = True
        return handlers.mail_handler.send_mail(self.mail_view_name, **mail_kwargs)
