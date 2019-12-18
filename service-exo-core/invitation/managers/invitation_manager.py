from django.db.models import Manager, Q
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from datetime import datetime

from utils.descriptors import CustomFilterDescriptorMixin
from utils.dates import increase_date

from ..conf import settings


class InvitationManager(CustomFilterDescriptorMixin, Manager):

    FILTER_DESCRIPTORS = [
        {
            'field': 'status',
            'options': settings.INVITATION_CH_STATUS,
        }, {
            'field': 'type',
            'options': settings.INVITATION_CH_TYPE,
        },
    ]

    def filter_by_status_not_cancelled(self):
        return self.exclude(status=settings.INVITATION_STATUS_CH_CANCELLED)

    def filter_by_status(self, status):
        if type(status) == list:
            q_filter = Q(status__in=status)
        else:
            q_filter = Q(status=status)

        return self.filter(q_filter).distinct()

    def filter_by_type(self, filter_type):
        return self.filter(type=filter_type)

    def _calculate_expiration_day(self, days=None):
        if days is None:
            return None
        now = timezone.now()
        today = datetime(now.year, now.month, now.day)
        expiration_day = increase_date(days=days, date=today)
        return expiration_day.date()

    def _create_invitation(
        self, user_from, user_to, related_object,
        invitation_type, days=None, *args, **kwargs
    ):
        """
            Generic function for creating a new invitation,
            and related object too.
        """
        invitation = self.model.objects.create(
            type=invitation_type,
            user=user_to,
            invite_user=user_from,
            valid_date=self._calculate_expiration_day(days),
            _description=kwargs.get('description', None),
            scope=kwargs.get('scope', None),
        )

        related_invitation = self.model.invitation_detail_class.objects.create(
            content_object=related_object,
            invitation=invitation,
        )

        if kwargs.get('autosend', True) or kwargs.get('autosend') is None:
            related_invitation.send_notification(user_from)
        else:
            related_invitation.skip_notification()

        if kwargs.get('status'):
            status = kwargs.get('status')
            if status == settings.INVITATION_STATUS_CH_ACTIVE:
                invitation.accept(invitation.user)
            elif status == settings.INVITATION_STATUS_CH_CANCELLED:
                invitation.cancel(invitation.user)

        return invitation

    def create_role_invitation(
            self, user_from, user_to, role, days=None, *args, **kwargs
    ):
        """
        Creates an invitation from an user to another user, with a role.
        - user_from: user that create the invitation
        - user_to: user invited
        - role: CustomerUserRole/ConsultantProjectRole/UserProjectRole object,
        created previously
        - days: expiration in days from now. Can be null, for no expiration
        invitation
        """
        return self._create_invitation(
            user_from,
            user_to,
            role,
            settings.INVITATION_TYPE_ROLES,
            days,
            scope=getattr(role, 'project', None),
            *args, **kwargs
        )

    def create_consultant_validation_invitation(
            self, user_from, user_to, validation_obj,
            *args, **kwargs
    ):
        """
        Creates an User invitation for any Consultant Validation item like:
            - SkillAssessment
            - Agreement
            - Test
            - Application
        """
        return self._create_invitation(
            user_from=user_from,
            user_to=user_to,
            related_object=validation_obj,
            invitation_type=validation_obj.validation_type,
            *args, **kwargs
        )

    def create_simple_signup_invitation(
            self, from_user, user, *args, **kwargs
    ):
        """
        Create a Simple Invitation for one User in order to activate
        itself once, the password is defined by itself.
        """
        return self._create_invitation(
            user_from=from_user,
            user_to=user,
            related_object=user,
            invitation_type=settings.INVITATION_TYPE_SIMPLE_SIGNUP,
            *args, **kwargs
        )

    def create_team_invitation(
            self, from_user, to_user, related_object, *args, **kwargs
    ):
        """
        Simple SignUp for users without Contract neither other kind of
        previous steps. Users only will need to define a password using
        the email sent and will be activated after that.
        Used to add new Members to Sprints Teams
        """
        return self._create_invitation(
            user_from=from_user,
            user_to=to_user,
            related_object=related_object,
            invitation_type=settings.INVITATION_TYPE_TEAM,
            scope=related_object,
            *args, **kwargs
        )

    def create_survey_invitation(self, user_from, user_to, survey, days=None):
        """
        Creates an invitation from an user to another user, with a survey.
            - user_from: user that create the invitation
            - user_to: user invited
            - survey: SurveyDetail object, created previously
            - days: expiration in days from now. Can be null, for no expiration
            invitation
        """
        return self._create_invitation(
            user_from=user_from,
            user_to=user_to,
            related_object=survey,
            invitation_type=settings.INVITATION_TYPE_SURVEY,
            days=days,
        )

    def create_applicant_invitation(
            self, from_user, to_user, related_object, *args, **kwargs
    ):
        """
        Invitation for consultant who have been invited to applicant the ticket
        related_object is an Applicant object
        """
        return self._create_invitation(
            user_from=from_user,
            user_to=to_user,
            related_object=related_object,
            invitation_type=settings.INVITATION_TYPE_TICKET,
            *args, **kwargs
        )

    def create_user_agreement(self, from_user, to_user, related_object):
        return self._create_invitation(
            user_from=from_user,
            user_to=to_user,
            related_object=related_object,
            invitation_type=settings.INVITATION_TYPE_AGREEMENT,
            autosend=False,
        )

    def from_user(self, user):
        """
        Filter by invite_user
        """
        return self.filter(invite_user=user)

    def to_user(self, user):
        """
        Filter by user
        """
        return self.filter(user=user)

    def filter_by_object(self, object_related):
        """
        Filter by invitation related object
        """
        try:
            obj_ct = ContentType.objects.get_for_model(object_related)
            return self.filter(
                invitation_objects__content_type__pk=obj_ct.id,
                invitation_objects__object_id=object_related.id,
            )
        except AttributeError:
            return self.none()
