from django.conf import settings
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.utils.cache import patch_vary_headers


class LocaleMiddleware(MiddlewareMixin):

    def process_request(self, request):
        language_from_request = request.GET.get('lang', None)
        if not language_from_request:
            language = settings.LANGUAGE_CODE
        else:
            language = language_from_request
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        language = translation.get_language()
        patch_vary_headers(response, ('Accept-Language',))
        response.setdefault('Content-Language', language)
        return response
