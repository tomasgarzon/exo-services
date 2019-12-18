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
        content = request.FILES.get('file').read()
        temp_file = tempfile.mktemp(suffix='.json')
        with open(temp_file, 'a') as dump_fd:
            dump_fd.write(content.decode())
        call_command('loaddata', temp_file)
        return Response({'status': 'ok'})


class PopulatorAPIView(views.APIView):
    renderer_classes = (renderers.JSONRenderer, )
    parser_classes = (parsers.JSONParser, )

    def post(self, request, format=None):
        """
        Example of use:
        curl -X POST -d '{"n": "2", "uuid": "4f618e67-7ce4-49ab-959c-6a0b8411e0c1"}'
        -H "Content-Type: application/json"  http://localhost:8003/populator/
        """
        number = request.data.get('n')
        uuid = request.data.get('uuid')
        call_command('create_fake_opportunities', '-n', number, '-u', uuid)
        return Response({'status': 'ok'})
