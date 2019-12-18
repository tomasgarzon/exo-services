import tempfile
import json

from rest_framework import views, renderers, parsers
from rest_framework.response import Response

from django.core.management import call_command


class BackupAPIView(views.APIView):
    renderer_classes = (renderers.JSONRenderer, )
    parser_classes = (parsers.JSONParser, parsers.FileUploadParser,)

    def get(self, request, format=None):
        temp_file = tempfile.mktemp(suffix='.json')
        call_command('dumpdata', '-o', temp_file)
        with open(temp_file, 'r') as dump_fd:
            content = json.loads(dump_fd.read())
        return Response(content)

    def post(self, request, format=None):
        # curl -X POST -H "Content-Type: application/octet-stream" -H "Content-Disposition:inline;filename=salida.json" --data-binary @salida.json  http://localhost:8002/backup/  # noqa
        content = request.FILES.get('file').read()
        temp_file = tempfile.mktemp(suffix='.json')
        with open(temp_file, 'a') as dump_fd:
            dump_fd.write(content.decode())
        call_command('loaddata', temp_file)
        return Response({'status': 'ok'})
