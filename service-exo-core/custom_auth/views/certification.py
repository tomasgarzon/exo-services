from django.views.generic.base import RedirectView
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from project.models import Project


class JoinLevel1View(LoginRequiredMixin, RedirectView):
    model = Project
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        url = settings.DOMAIN_NAME
        language = kwargs.get('language', 'en')
        project_id = settings.PROJECT_CERTIFICATION_LEVEL_1_LANGUAGE.get(language)

        try:
            project = self.model.objects.get(pk=project_id)
        except Exception:
            project = None
        if project:
            team = project.teams.first()
            team.add_member(
                user_from=project.created_by,
                email=user.email,
                name=user.short_name,
            )
            url += project.get_frontend_index_url(user)
        return url
