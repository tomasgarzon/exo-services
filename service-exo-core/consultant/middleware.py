from django.conf import settings
from django.http.response import HttpResponseRedirect

from functools import reduce


class ConsultantActivationMiddleware:
    """https://docs.djangoproject.com/en/1.11/topics/http/middleware/"""
    PATHS_EXCLUDED = [
        'auth', 'invitations', 'signup', 'password',
        'api', 'ws', 'assets', 'media',
        'accounts', 'profile2']
    EXTENSIONS_EXCLUDED = ['js', 'map', 'css']

    def __init__(self, get_response):
        self.get_response = get_response

    def path_is_excluded(self, path):
        path_startswith = reduce(
            (lambda x, y: x | y),
            (map(lambda x: path.startswith(x, 1), self.PATHS_EXCLUDED)),
        )
        path_endwith = reduce(
            (lambda x, y: x | y),
            (map(lambda x: path.endswith(x, 1), self.EXTENSIONS_EXCLUDED)),
        )
        return path_endwith or path_startswith

    def check_consultant_activation(self, request):
        url = None
        if request.user.is_authenticated:
            user = request.user
            if user.is_consultant:
                consultant = request.user.consultant
                if not consultant.has_registration_process_finished:
                    url = consultant.registration_process_current_url
                elif consultant.is_in_waiting_list:
                    if request.path != consultant.get_public_profile_v2():
                        url = consultant.get_public_profile_v2()
                elif consultant.has_tos_invitations_pending:
                    url = settings.FRONTEND_INVITATION_PAGE.format(
                        **{'hash': consultant.get_tos_invitation_pending().hash},
                    )
        return url

    def __call__(self, request):
        if not self.path_is_excluded(request.path):
            url = self.check_consultant_activation(request)
            if url is not None:
                return HttpResponseRedirect(url)
        response = self.get_response(request)

        return response
