import unittest

from local import EXOLEVER_HOST

import requests


class OpportunityTest(unittest.TestCase):
    def do_login(self):
        url = '/api/accounts/login/'
        prefix = ''
        url = EXOLEVER_HOST + prefix + url
        data = {
            'username': 'gorkaarrizabalaga@example.com',
            'password': '.eeepdExO'
        }
        return requests.post(url, data)

    def get_opportunities(self, user):
        url = '/api/opportunity/'
        prefix = '/opportunities'
        url = EXOLEVER_HOST + prefix + url
        headers = {'Authorization': user}
        return requests.get(url, headers=headers)

    def get_opportunity_detail(self, token, pk):
        url = '/api/opportunity/{}/'.format(pk)
        prefix = '/opportunities'
        url = EXOLEVER_HOST + prefix + url
        headers = {'Authorization': token}
        return requests.get(url, headers=headers)

    def get_token(self):
        login_data = self.do_login()
        user = login_data.json().get('token')
        token = 'Bearer ' + user
        return token

    def create_message(self, opportunity_id, token):
        url = '/api/opportunity/{}/create_conversation/'.format(opportunity_id)
        prefix = '/opportunities'
        url = EXOLEVER_HOST + prefix + url
        headers = {'Authorization': token}
        data = {'message': 'hello'}
        return requests.post(url, data=data, headers=headers)

    def get_agreements(self, token):
        url = '/api/marketplace/agreement/'
        url = EXOLEVER_HOST + url
        headers = {'Authorization': token}
        return requests.get(url, headers=headers)

    def get_conversations(self, token, uuid):
        url = '/api/{}/conversations/'.format(uuid)
        prefix = '/conversations'
        url = EXOLEVER_HOST + prefix + url
        headers = {'Authorization': token}
        return requests.get(url, headers=headers)

    def test_do_login(self):
        response = self.do_login()
        self.assertEqual(response.status_code, 200)

    def test_accept_marketplace_agreement(self):
        token = self.get_token()
        response = self.get_agreements(token)
        agreement_pk = response.json()[0].get('pk')
        self.assertEqual(response.status_code, 200)
        url = EXOLEVER_HOST + '/api/marketplace/agreement/{}/accept/'.format(agreement_pk)
        response = requests.post(url, headers={'Authorization': token})
        self.assertEqual(response.status_code, 200)
        response = self.get_opportunities(token)
        self.assertEqual(response.status_code, 200)

    def test_get_opportunities(self):
        token = self.get_token()
        response = self.get_opportunities(token)
        self.assertEqual(response.status_code, 200)

    def test_create_message(self):
        token = self.get_token()
        response = self.get_opportunities(token)
        self.assertEqual(response.status_code, 200)
        response = self.get_opportunity_detail(token, 1)
        self.assertEqual(response.status_code, 200)
        opportunity = response.json()
        response = self.create_message(opportunity['id'], token)
        self.assertEqual(response.status_code, 200)
        response = self.get_conversations(token, opportunity['uuid'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
