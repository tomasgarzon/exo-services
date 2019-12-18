import unittest

from local import EXOLEVER_HOST

import requests


class ChatUserTest(unittest.TestCase):
    def do_login(self):
        url = '/api/accounts/login/'
        prefix = ''
        url = EXOLEVER_HOST + prefix + url
        data = {
            'username': 'gorkaarrizabalaga@example.com',
            'password': '.eeepdExO'
        }
        return requests.post(url, data)

    def get_messages(self, token, user_to=None):
        url = '/api/conversations/'
        prefix = '/conversations'
        url = EXOLEVER_HOST + prefix + url
        headers = {'Authorization': token}
        params = {}
        if user_to:
            params['user_to'] = user_to
        return requests.get(url, params=params, headers=headers)

    def get_user_detail(self, token, slug):
        url = '/api/profile-public/{}/'.format(slug)
        prefix = ''
        url = EXOLEVER_HOST + prefix + url
        headers = {'Authorization': token}
        return requests.get(url, headers=headers)

    def get_token(self):
        login_data = self.do_login()
        user = login_data.json().get('token')
        token = 'Bearer ' + user
        return token

    def test_start_conversation(self):
        token = self.get_token()
        response = self.get_user_detail(token, 'naina-lavrova')
        self.assertEqual(response.status_code, 200)
        user_pk = response.json().get('pk')
        url = EXOLEVER_HOST + '/api/profile/{}/start-conversation/'.format(user_pk)
        data = {'message': 'hello', 'files': []}
        response = requests.post(url, data=data, headers={'Authorization': token})
        self.assertEqual(response.status_code, 201)
        response = self.get_messages(token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json(), 1))

        response = self.get_messages(token, user_to=response.json().get('uuid'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json(), 1))
