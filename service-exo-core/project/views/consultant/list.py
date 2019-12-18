from django.conf import settings
from django.http.response import HttpResponseRedirect
from django.contrib import messages

from utils.generic.list import ListFilterView
from project.views.mixin import ProjectPermissionMixin, ProjectQuerySetListView
from relation.models import ConsultantProjectRole
from invitation.models import Invitation

from ...forms import ConsultantSearchListForm


class ConsultantListView(
        ProjectPermissionMixin,
        ProjectQuerySetListView,
        ListFilterView
):
    template_name = 'project/consultants/list.html'
    model = ConsultantProjectRole
    paginate_by = 50
    filter_form_class = ConsultantSearchListForm
    project_permission_required = settings.PROJECT_PERMS_PROJECT_MANAGE_CONSULTANT
    bulk_action_list = [
        ('send_notification', 'Send invitation'),
    ]

    def send_notification(self, objects):
        related_objects = self.model.objects.filter(
            id__in=objects.split(','),
        )
        for role in related_objects:
            try:
                invitation = Invitation.objects.filter_by_object(role).get()
                invitation.invitation_related.send_notification(self.request.user)
            except Invitation.DoesNotExist:
                pass
        messages.success(self.request, 'Notifications sent successfully')
        return HttpResponseRedirect('.')
