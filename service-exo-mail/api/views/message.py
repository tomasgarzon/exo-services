from rest_framework import viewsets, renderers, parsers

from ..serializers.message import SendMailSerializer, ConfigMailSerializer


class SendMailViewSet(viewsets.ModelViewSet):
    serializer_class = SendMailSerializer
    renderer_classes = (renderers.JSONRenderer, )
    parser_classes = (parsers.MultiPartParser, parsers.JSONParser)
    http_method_names = ['post']


class ConfigMailViewSet(viewsets.ModelViewSet):
    serializer_class = ConfigMailSerializer
    http_method_names = ['post']
