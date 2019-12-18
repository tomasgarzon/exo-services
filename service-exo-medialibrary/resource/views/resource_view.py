from django.views.generic import View
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.conf import settings


class ResourceRedirectView(View):
    def get(self, request, *args, **kwargs):
        handle = kwargs.get('handle', '')
        filename = kwargs.get('filename', '')

        if settings.DEBUG:
            url = 'https://{}/{}'.format(settings.RESOURCE_FILESTACK_CDN_URL, handle)
            return HttpResponseRedirect(url)
        else:
            response = HttpResponse()
            response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
            url_redirect = '/{}/{}/{}'.format(
                settings.INTERNAL_REDIRECT,
                settings.RESOURCE_FILESTACK_CDN_URL,
                handle)
            response['X-Accel-Redirect'] = url_redirect
            return response
