import datetime
import unittest

from local import EXOLEVER_HOST

import requests


class EventWebsiteTest(unittest.TestCase):
    def do_login(self):
        url = '/api/accounts/login/'
        prefix = ''
        url = EXOLEVER_HOST + prefix + url
        data = {
            'username': 'qa@openexo.com',
            'password': '.eeepdExO'
        }
        return requests.post(url, data)

    def create_event(self, token):
        url = '/api/event/'
        prefix = '/events'
        url = EXOLEVER_HOST + prefix + url
        headers = {'Authorization': token, 'Content-type': 'application/json'}
        data = {
            'title': 'Rerum iusto nemo.',
            'sub_title': 'Amet natus voluptate ut delectus ad.',
            'description': 'Beatae eveniet tempora quaerat doloribus reiciendis.',
            'start': datetime.date(2019, 6, 6).isoformat(),
            'end': datetime.date(2019, 6, 6).isoformat(),
            'type_event': 'W',
            'follow_type': ['S'],
            'location': 'Adrianshire, Montenegro',
            'url': 'http://brown.com/',
            'languages': ['english'],
            'show_price': True,
            'amount': '948',
            'currency': 'E',
            'organizers': [{
                'name': 'Joseph Hodgson',
                'email': 'nichollsmichelle@yahoo.com',
                'url': 'https://jackson.com/faq.php'}],
            'participants': []}
        return requests.post(url, json=data, headers=headers)

    def get_landing_page(self, token, event_uuid):
        url = 'api/landing/page/{}/'.format(event_uuid)
        prefix = '/website'
        url = EXOLEVER_HOST + prefix + url
        headers = {'Authorization': token}
        return requests.get(url, headers=headers)

    def get_token(self):
        login_data = self.do_login()
        user = login_data.json().get('token')
        token = 'Bearer ' + user
        return token

    def test_do_login(self):
        response = self.do_login()
        self.assertEqual(response.status_code, 200)

    def test_create_event(self):
        # PREPARE DATA
        token = self.get_token()
        # DO ACTION
        response = self.create_event(token)
        # ASSERTS
        self.assertEqual(response.status_code, 201)

    def test_get_website(self):
        # PREPARE DATA
        token = self.get_token()
        response = self.create_event(token)
        event_uuid = response.json().get('uuid')
        response = self.get_landing_page(token, event_uuid)
        self.assertEqual(response.status_code, 200)
