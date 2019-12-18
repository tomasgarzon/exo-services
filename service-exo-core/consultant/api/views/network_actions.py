import logging

from rest_framework import views
from guardian.mixins import PermissionRequiredMixin as GuardianPermissionRequiredMixin
from rest_framework.response import Response

from django.views.generic.detail import SingleObjectMixin
from django.conf import settings
from django.urls import reverse
from django.db.models.deletion import ProtectedError
from django.contrib.auth.mixins import PermissionRequiredMixin

from project.models import Project
from sprint.models import Sprint
from team.models import Team
from customer.models import Customer
from utils.drf import SuccessMessageMixin

from ...models import Consultant
from ..serializers.consultant_create import ConsultantSerializer, ConsultantCreatedSerializer


BLOCK_MODELS = [Project, Sprint, Team, Customer]
logger = logging.getLogger('network')


class ConsultantActionMixinView(
        GuardianPermissionRequiredMixin,
        SuccessMessageMixin,
        SingleObjectMixin,
        views.APIView):

    permission_required = settings.CONSULTANT_PERMS_CONSULTANT_EDIT_PROFILE
    return_404 = True
    model = Consultant

    def get_queryset(self):
        return self.model.all_objects.all()

    def check_permissions(self, request):
        has_network_perms = request.user.has_perm(
            settings.CONSULTANT_FULL_PERMS_CONSULTANT_LIST_AND_EXPORT)
        if has_network_perms:
            return None
        return super().check_permissions(request)


class DeleteConsultantView(ConsultantActionMixinView):

    success_message = 'Consultant deleted successfully'

    def get(self, request, pk, format='json'):
        consultant = self.get_object()
        can_delete = True
        try:
            collector = consultant.get_instances_related()
            consultant.user.get_instances_related(collector)
        except ProtectedError:
            can_delete = False
        if can_delete:
            for model in BLOCK_MODELS:
                if model in collector.data.keys():
                    can_delete = False
                    break
        if can_delete:
            logger.info('Consultant: {} deleted by: {}'.format(
                request.user,
                consultant,
            ))
            for model, instances in collector.data.items():
                logger.info('{} {} deleted'.format(
                    str(model),
                    len(instances),
                ))
                for k in instances:
                    logger.info('{} {}'.format(str(k.__class__), str(k.pk)))
            # Delete user and therefore consultant
            try:
                consultant.user.delete()
                consultant.delete()
            except Exception:
                pass
            self.set_success_message({})
            success_url = request.META.get('HTTP_REFERER')
            return Response({
                'status': 'deleted',
                'url': success_url,
            })
        else:
            logger.info('Consultant: {} cannot be deleted by {}'.format(
                consultant,
                request.user,
            ))
            disable_url = reverse('consultant:disable', args=[pk])
            return Response({
                'status': 'not-deleted',
                'url': disable_url,
            })


class ReactivateConsultantView(ConsultantActionMixinView):

    success_message = 'Consultant has been activated successfully'

    def get(self, request, pk, format='json'):
        consultant = self.get_object()
        consultant.reactivate(self.request.user)
        self.set_success_message({})
        logger.info('Consultant: {} reactivated by: {}'.format(
            request.user,
            consultant,
        ))
        return Response({
            'status': 'ok',
        })


class ConsultantAddView(
        PermissionRequiredMixin,
        views.APIView):

    serializer_class = ConsultantSerializer
    permission_required = settings.CONSULTANT_FULL_PERMS_ADD_CONSULTANT
    raise_exception = True

    def post(self, request, format='json'):
        serializer = self.serializer_class(
            data=request.data, context={'view': self})
        serializer.is_valid(raise_exception=True)
        consultant = serializer.save(user_from=request.user)
        serializer = ConsultantCreatedSerializer(instance=consultant)
        return Response(serializer.data)
