from django.urls import reverse

from guardian.shortcuts import get_objects_for_user

from project.helpers import next_project_url
from project.external_projects import get_projects

from .conf import settings


class UserRedirectController:

    @staticmethod
    def redirect_url(user):
        url = None
        zone = False

        if user.is_consultant:
            consultant = user.consultant
            if not consultant.has_registration_process_finished:
                url = consultant.registration_process_current_url
            elif consultant.is_in_waiting_list:
                url = consultant.get_public_profile_v2()
            elif consultant.has_tos_invitations_pending:
                url = settings.FRONTEND_INVITATION_PAGE.format(
                    **{'hash': consultant.get_tos_invitation_pending().hash})
            else:
                url = settings.FRONTEND_CIRCLES_PAGE
        elif user.is_superuser or user.is_staff:
            zone = True
            url = reverse('dashboard:home')
        else:
            projects = get_objects_for_user(
                user, settings.PROJECT_FULL_VIEW, with_superuser=False,
            )
            if projects:
                project = projects.order_by('-start').first()
                url, zone = next_project_url(project, user)
            else:
                projects = get_projects(user)
                if projects:
                    url = projects[0]['url']
                else:
                    url = settings.FRONTEND_CIRCLES_PAGE
        return url, zone
