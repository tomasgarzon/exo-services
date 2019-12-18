from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext, TemplateDoesNotExist
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login

from guardian.conf import settings as guardian_settings

from .shortcuts import has_project_perms, has_team_perms


def display_error(request, return_403, login_url, redirect_field_name):
    if return_403:
        if guardian_settings.RENDER_403:
            try:
                response = render_to_response(
                    guardian_settings.TEMPLATE_403, {},
                    RequestContext(request),
                )
                response.status_code = 403
                return response
            except TemplateDoesNotExist as e:
                if settings.DEBUG:
                    raise e
        elif guardian_settings.RAISE_403:
            raise PermissionDenied
        return HttpResponseForbidden()
    else:
        return redirect_to_login(
            request.get_full_path(),
            login_url,
            redirect_field_name,
        )


def get_project_403_or_None(
        request, perms, project, obj=None, login_url=None,
        redirect_field_name=None, return_403=False, accept_global_perms=False,
):
    login_url = login_url or settings.LOGIN_URL
    redirect_field_name = redirect_field_name or REDIRECT_FIELD_NAME

    # Handles both original and with object provided permission check
    # as ``obj`` defaults to None

    has_permissions = has_project_perms(
        project,
        perms,
        request.user,
        related=obj,
    )

    if not has_permissions:
        return display_error(request, return_403, login_url, redirect_field_name)


def get_team_403_or_None(
        request, perms, team, obj=None, login_url=None,
        redirect_field_name=None, return_403=False, accept_global_perms=False,
):
    login_url = login_url or settings.LOGIN_URL
    redirect_field_name = redirect_field_name or REDIRECT_FIELD_NAME

    # Handles both original and with object provided permission check
    # as ``obj`` defaults to None

    has_permissions = has_team_perms(
        team,
        perms,
        request.user,
        related=obj,
    )

    if not has_permissions:
        return display_error(request, return_403, login_url, redirect_field_name)
