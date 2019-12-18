from django.conf import settings
from django.core.exceptions import RequestDataTooBig

from djangorestframework_camel_case.parser import CamelCaseJSONParser as OriginalCamelCaseJSONParser

from rest_framework import parsers, renderers


def check_content_length(parser_context):

    if parser_context and settings.DATA_UPLOAD_MAX_MEMORY_SIZE and 'request' in parser_context:

        try:
            content_length = int(parser_context['request'].META.get('CONTENT_LENGTH', 0))
        except (ValueError, TypeError):
            content_length = 0

        if content_length and content_length > settings.DATA_UPLOAD_MAX_MEMORY_SIZE or content_length < 0:
            raise RequestDataTooBig('Request body exceeded settings.DATA_UPLOAD_MAX_MEMORY_SIZE.')


class LimitedJSONParser(parsers.JSONParser):
    """
    Parses JSON-serialized data.
    This json parser won't allow large file uploads through base64 encoded strings. Use multipart instead
    """
    media_type = 'application/json'
    renderer_class = renderers.JSONRenderer

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as JSON and returns the resulting data.
        """
        check_content_length(parser_context)

        return super(LimitedJSONParser, self).parse(stream, media_type, parser_context)


class LimitedFormParser(parsers.FormParser):
    """
    Parser for form data.
    This parser won't allow large file uploads through urlencoded encoded strings. Use multipart instead
    """
    media_type = 'application/x-www-form-urlencoded'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as a URL encoded form,
        and returns the resulting QueryDict.
        """
        check_content_length(parser_context)

        return super(LimitedFormParser, self).parse(stream, media_type, parser_context)


class CamelCaseJSONParser(OriginalCamelCaseJSONParser):
    def parse(self, stream, media_type=None, parser_context=None):
        check_content_length(parser_context)

        return super(CamelCaseJSONParser, self).parse(stream, media_type, parser_context)
