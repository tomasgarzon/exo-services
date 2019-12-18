from django.http import Http404

from consultant.models import ContractingData

from ..serializers.contracting import ContractingDataSerializer
from .profile_mixin import UpdateProfileMixin


class UpdateContractingView(UpdateProfileMixin):
    """
    Use this endpoint to change user email.
    """
    serializer_class = ContractingDataSerializer
    swagger_schema = None

    def get_serializer(self, instance, *args, **kwargs):
        if not instance.is_consultant:
            raise Http404
        contracting_area, _ = ContractingData.objects.get_or_create(
            profile=instance.consultant.exo_profile,
        )
        return super().get_serializer(contracting_area, *args, **kwargs)
