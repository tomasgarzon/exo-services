import json

from django.core.management.base import BaseCommand

from ...models import Resource, Tag


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', nargs='+', type=str)

    def update_resources_from_csv(self, path):
        resources_updated = []
        resources_new = []

        with open(path, 'r') as json_data:
            data = json.load(json_data)

            for item in data:
                link = item.get('link')

                try:
                    resource = Resource.objects.get(link=link)
                    resources_updated.append(link)
                except Resource.DoesNotExist:
                    resources_new.append(link)
                    resource = Resource(link=link)

                resource.name = item.get('name')
                resource.description = item.get('description')
                resource.url = item.get('url')
                resource.status = item.get('status')
                resource.thumbnail = item.get('thumbnail')
                resource.duration = item.get('duration')
                resource.sections = item.get('sections')
                resource.projects = ','.join(item.get('projects') or [])
                tags = [tag['name'] for tag in item.get('tags') or []]
                resource.type = item.get('type')
                resource.extra_data = item.get('extra_data')
                resource.save()
                resource.tags.add(*list(Tag.objects.filter(name__in=tags)))

        self.stdout.write(
            'Resouces found: {}'.format(len(resources_updated)))
        self.stdout.write(
            'New Resouces: {}'.format(len(resources_new)))

    def handle(self, *args, **kwargs):
        # Params
        file = kwargs.get('file')[0]
        self.update_resources_from_csv(file)
