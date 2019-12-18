import requests

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model

from ...helpers import update_or_create_badge


class Command(BaseCommand):

    def _request_marketplace_badges(self):
        host = settings.EXOLEVER_HOST + settings.SERVICE_EXO_OPPORTUNITIES_HOST
        path = 'api/opportunity-badges/'
        url = host + path
        headers = {
            'USERNAME': settings.AUTH_SECRET_KEY
        }
        return requests.get(url, headers=headers)

    def handle(self, *args, **options):
        response = self._request_marketplace_badges()

        assert response.status_code == requests.codes.ok

        for item in response.json():
            code = item.get('code')
            title = item.get('title')
            date = item.get('startDate')
            users = item.get('users')
            category = item.get('category')

            item = {
                'name': title,
                'date': date,
            }

            for user_uuid in users:
                user = get_user_model().objects.get(uuid=user_uuid)
                update_or_create_badge(
                    user_from=user,
                    user_to=user,
                    code=code,
                    category=category,
                    items=[item],
                    description='sync-marketplace-badges')
