from django.http.response import HttpResponseRedirect
from django.contrib import messages

from utils.generic.list import ListFilterView
from project.views.mixin import ProjectPermissionMixin, ProjectQuerySetListView
from invitation.models import Invitation
from relation.models import UserProjectRole

from ...models import Team
from ...forms.team import TeamSearchListForm


class TeamListView(
        ProjectPermissionMixin,
        ProjectQuerySetListView,
        ListFilterView
):
    template_name = 'sprint/team/team_list.html'
    model = Team
    paginate_by = 10
    filter_form_class = TeamSearchListForm
    bulk_action_list = [
        ('send_notification', 'Send invitation'),
        ('email_teams', 'Email the teams'),
    ]

    def send_notification(self, objects):
        related_objects = self.model.objects.filter(
            id__in=objects.split(','),
        )
        roles = UserProjectRole.objects.filter(
            user__teams__in=related_objects,
        ).distinct()
        for role in roles:
            invitations = Invitation.objects.filter_by_object(role)
            for invitation in invitations:
                invitation.invitation_related.send_notification(self.request.user)

        messages.success(self.request, 'Notifications sent successfully')
        return HttpResponseRedirect('.')

    def email_teams(self, objects):
        pass
