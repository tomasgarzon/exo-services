from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.urls import reverse

from rest_framework.test import APIClient

from resource.models import Resource

import yaml


class Command(BaseCommand):
    help = (
        'Populate service-exo-medialibrary'
    )
    filename = '/populator/data/medialibrary.json'
    files_path = '/populator/data/projects.yml'

    def handle(self, *args, **options):
        assert settings.POPULATOR_MODE
        self.stdout.write('\n Populating {}: \n\n'.format(settings.SERVICE_NAME))
        self.stdout.write('\n Populating tags and categories')
        call_command('import_tags_and_categories')
        path = '{base_dir}{file_path}'.format(
            base_dir=settings.BASE_DIR, file_path=self.filename)
        call_command('update_resources_tags_and_projects', '-f', path)
        self.stdout.write('\n Populating resources')
        path = '{base_dir}{file_path}'.format(
            base_dir=settings.BASE_DIR, file_path=self.files_path)
        client = APIClient()
        client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)
        url_api = reverse('api:resources:post-save-project')
        self.stdout.write('\n Populating projects')
        with open(path, 'r') as file_obj:
            data = yaml.load(file_obj, Loader=yaml.Loader)
            projects = data.get('projects')
            for project in projects:
                project_type = project.get('type')
                project_uuid = project.get('uuid')
                data = {
                    'uuid': project_uuid,
                    'type_project_lower': project_type,
                }
                response = client.post(url_api, data=data)
                assert response.status_code == 200
                for resource_node in project.get('resources', []):
                    resource = Resource.objects.get(name=resource_node.get('name'))
                    url = reverse(
                        "api:resources:library-add-to-projects",
                        kwargs={'pk': resource.pk})
                    response = client.put(url, data={'uuid': project_uuid})

                    assert response.status_code == 200

        self.stdout.write('\n Populated {}: \n\n'.format(settings.SERVICE_NAME))
