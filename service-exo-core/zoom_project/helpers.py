import logging
import requests
from requests import exceptions

from .conf import settings


logger = logging.getLogger('zoom')

SHARED_KEY = 'A5GGLDymZ7vCfjjy'


class ZoomUsHelper:

    def get_meeting(self, meeting_id):
        """
            Get meeting object for a meeting_id
        """
        if not getattr(settings, 'ZOOM_URL'):
            logging.info('Zoom service not configured yet')
            return None
        data = {
            'key': SHARED_KEY,
            'zoom_key': self.zoom_api_key,
            'zoom_secret': self.zoom_secret_key,
            'meeting_id': meeting_id}
        logging.info('Calling to zoom service {}'.format(data))
        url = settings.ZOOM_URL + '/zoom_url/'
        try:
            response = requests.post(url, json=data)
            logging.info('Zoom get successfully {}'.format(response.json()))
            return response.json().get('url')
        except exceptions.RequestException as e:
            logging.error('Request error {}'.format(e))
        if not response.ok:
            logging.error('Request error {}'.format(response.content))

        return None

    def schedule_meeting(self, meeting_id, title, start, timezone, duration):
        """
            Get meeting object for a meeting_id
        """
        if not getattr(settings, 'ZOOM_URL'):
            logging.info('Zoom service not configured yet')
            return None
        data = {
            'key': SHARED_KEY,
            'zoom_key': self.zoom_api_key,
            'zoom_secret': self.zoom_secret_key,
            'meeting_id': meeting_id.replace(' ', '').replace('-', ''),
            'title': title,
            'start': start,
            'timezone': timezone,
            'duration': duration}
        logging.info('Calling to zoom service {}'.format(data))
        url = settings.ZOOM_URL + '/schedule_meeting/'
        try:
            response = requests.post(url, json=data)
            logging.info('Zoom schedule meeting successfully {}'.format(response.json()))
            return response.json()
        except exceptions.RequestException as e:
            logging.error('Request error {}'.format(e))
        if not response.ok:
            logging.error('Request error {}'.format(response.content))

        return None

    def get_meeting_token(self, meeting_id):
        zoom_token = None
        zoom_split_keyword = settings.ZOOM_PROJECT_TOKEN_NAME
        meeting_url = self.get_meeting(meeting_id)

        if meeting_url:
            zoom_token = meeting_url.split(
                '{}='.format(zoom_split_keyword))[1]

        return zoom_token

    def get_schedule_meeting(self, meeting_id, title, start, timezone, duration):
        zoom_split_keyword = settings.ZOOM_PROJECT_TOKEN_NAME
        response = self.schedule_meeting(
            meeting_id, title, start, timezone, duration)

        if response:
            values = {}
            values['start_url'] = response['url']['start_url'].split(
                '{}='.format(zoom_split_keyword))[1]
            values['id'] = response['url']['id']
            return values
        return None
