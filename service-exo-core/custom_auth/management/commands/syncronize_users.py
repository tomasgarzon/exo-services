import requests
import json

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings


URL_MIGRATE_AUTH = 'api/migrate/'


class Command(BaseCommand):
    help = (
        'Sync users with service-exo-auth'
    )

    def get_authorization_header(self):
        return {'USERNAME': settings.AUTH_SECRET_KEY}

    def get_url(self):
        return '{}{}{}'.format(
            settings.EXOLEVER_HOST,
            settings.SERVICE_EXO_AUTH_HOST,
            URL_MIGRATE_AUTH)

    def serialize_user(self, user):
        data = {}
        fields_to_migrate = [
            'uuid', 'password_updated', 'email', 'password',
            'date_joined', 'is_active', 'is_staff', 'is_superuser']
        for field in fields_to_migrate:
            value = getattr(user, field)
            if value is not None:
                data[field] = value.__str__()
        data['emails'] = []

        for email_address in user.emailaddress_set.all():
            email_data = {}
            for field in email_address._meta.fields:
                if field.name == 'user':
                    continue
                value = getattr(email_address, field.name)
                if value is not None:
                    email_data[field.name] = value.__str__()
            data['emails'].append(email_data)
        return data

    def handle(self, *args, **options):
        total_users = get_user_model().objects.all().count()
        header = self.get_authorization_header()
        url = self.get_url()
        if url is None:
            return
        start = 0
        while (start < total_users):
            end = start + 100
            users = get_user_model().objects.all()[start:end]
            data = []
            for user in users:
                data.append(self.serialize_user(user))
            self.stdout.write(json.dumps(data))
            response = requests.post(url, json=data, headers=header)
            assert response.status_code == requests.codes.ok
            start = end
