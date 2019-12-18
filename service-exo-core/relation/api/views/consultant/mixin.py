from django.conf import settings
from django.http import Http404

from braces.views import GroupRequiredMixin

from consultant.models import Consultant


class ConsultantMixin:

    def get_consultant(self):
        try:
            self.consultant = Consultant.all_objects.get(
                id=self.kwargs.get('consultant_pk'),
            )
            return self.consultant
        except Consultant.DoesNotExist:
            raise Http404


class ConsultantViewSetMixin(ConsultantMixin, GroupRequiredMixin):
    group_required = settings.REGISTRATION_GROUP_NAME

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
