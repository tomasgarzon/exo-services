from rest_framework.generics import get_object_or_404

from consultant.models import Consultant

from ..serializers.profile_consultant import (
    ConsultantProfileLanguagesSerializer,
    ConsultantProfileMTPSerializer,
    ConsultantCorePillarsSerializer,
    ConsultantProfileTimeAvailabilitySerializer,
    ConsultantProfileActivitiesSerializer,
    ConsultantProfileVideoSerializer,
)
from ..serializers.consultant_exo_attribute import ConsultantExOAttributesSerializer
from ..serializers.consultant_exo_industries import ConsultantIndustrySerializer
from ..serializers.consultant_keywords import ConsultantKeywordSerializer
from .profile_mixin import UpdateProfileMixin


class UpdateConsultantProfileMixin(UpdateProfileMixin):
    model = Consultant

    def get_consultant(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs.get('pk'))

    def get_permission_object(self):
        consultant = self.get_consultant()
        return consultant.user

    def get_queryset(self):
        return self.model.objects.all()


class UpdateConsultantExOProfileMixin(UpdateConsultantProfileMixin):

    def get_object(self):
        consultant = self.get_consultant()
        return consultant.exo_profile


class UpdateLanguagesProfileView(UpdateConsultantProfileMixin):
    """
    Use this endpoint to change languages profile.
    """
    serializer_class = ConsultantProfileLanguagesSerializer


class UpdateMTPProfileView(UpdateConsultantExOProfileMixin):
    serializer_class = ConsultantProfileMTPSerializer


class UpdateCorePillarsProfileView(UpdateConsultantProfileMixin):
    serializer_class = ConsultantCorePillarsSerializer


class UpdateTimeAvailabilityProfileView(UpdateConsultantExOProfileMixin):
    serializer_class = ConsultantProfileTimeAvailabilitySerializer


class UpdateActivitiesProfileView(UpdateConsultantExOProfileMixin):
    serializer_class = ConsultantProfileActivitiesSerializer


class UpdateExOAttributesProfileView(UpdateConsultantProfileMixin):
    serializer_class = ConsultantExOAttributesSerializer


class UpdateIndustryProfileView(UpdateConsultantProfileMixin):
    serializer_class = ConsultantIndustrySerializer


class UpdateKeywordProfileView(UpdateConsultantProfileMixin):
    serializer_class = ConsultantKeywordSerializer


class UpdateProfileVideoView(UpdateConsultantExOProfileMixin):
    serializer_class = ConsultantProfileVideoSerializer
