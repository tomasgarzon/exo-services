from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings

from ..models import Resource


class ResourceDownload(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        slug, _ = kwargs.get('slug').split('.')

        try:
            resource = Resource.objects.get(slug=slug)
        except Resource.MultipleObjectsReturned:
            resource = Resource.objects.filter(slug=slug)[0]

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            str(resource.file_name),
        )
        if settings.DEBUG:
            response.content = resource.read()
        else:
            response['X-Accel-Redirect'] = '/{}/{}{}/{}'.format(
                settings.INTERNAL_REDIRECT,
                settings.PROTECTED_URL,
                settings.FILES_S3_RESOURCE_FOLDER,
                str(resource._filename),
            )
        return response
