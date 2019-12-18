from mock import patch

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import authenticate

from utils.test_mixin import UserTestMixin
from utils.mails.handlers import mail_handler
from utils.faker_factory import faker


User = get_user_model()

FAKE_DATA = [
    {
        'uuid': 'af1813cf-fc30-497d-8814-a7e7e215aa5d',
        'password_updated': True,
        'email': 'hollybrooks@example.com',
        'password': 'pbkdf2_sha256$150000$SuBMzotwgSkP$W+eNt1Eke7QYODZF7cKBIsGwC+rY9XRkW3gp6Durv7c=',
        'date_joined': '2019-02-13 09:46:25.391262+00:00',
        'is_active': True,
        'is_staff': False,
        'is_superuser': False,
        'emails': [
            {
                'id': 88,
                'created': '2019-02-13 09:46:25.418581+00:00',
                'modified': '2019-02-13 09:46:25.418856+00:00',
                'email': 'hollybrooks@example.com',
                'verif_key': '1ff50333b20e4edf8bb06cfc798153c69a42f239',
                'verified_at': '2019-02-13 09:46:25.418641+00:00',
                'is_primary': True,
                'type_email': 'P'
            }
        ]
    },
    {
        'uuid': '1cd07dd7-4883-4838-9b5a-303ef0d6580c',
        'password_updated': True,
        'email': 'amyfinch@example.com',
        'password': 'pbkdf2_sha256$36000$fHpzKzDqARX3$UA2kCYkXdmBZmjcHbUt4zDiBtSO7WCVpQIzjVuLdNcE=',
        'date_joined': '2019-02-13 09:43:31.588344+00:00',
        'is_active': True,
        'is_staff': False,
        'is_superuser': False,
        'emails': [
            {
                'id': 9,
                'created': '2019-02-13 09:43:31.654886+00:00',
                'modified': '2019-02-13 09:43:31.655103+00:00',
                'email': 'amyfinch@example.com',
                'verif_key': '2ba012d4a78496bcf11c40b15bb2bc05b922aed5',
                'verified_at': '2019-02-13 09:43:31.654938+00:00',
                'is_primary': True,
                'type_email': 'P'
            }
        ]
    }
]


NEW_USER_FAKE = {
    'uuid': '03214e9c-1f6b-4b52-8080-c7b0103a5755',
    'password_updated': True,
    'email': 'jsonmoss@example.com',
    'password': 'pbkdf2_sha256$36000$fHpzKzDqARX3$UA2kCYkXdmBZmjcHbUt4zDiBtSO7WCVpQIzjVuLdNcE=',
    'date_joined': '2019-02-13 09:42:37.734438+00:00',
    'is_active': False,
    'is_staff': True,
    'is_superuser': True,
    'emails': [
        {
            'id': 10,
            'created': '2019-02-13 09:42:37.888346+00:00',
            'modified': '2019-02-13 09:42:37.888929+00:00',
            'email': 'jsonmoss@example.com',
            'verif_key': 'bf2da24f242eb9c0d82813f4f67755f59290f426',
            'verified_at': '2019-02-13 09:42:37.888643+00:00',
            'is_primary': True,
            'type_email': 'P'
        }
    ]
}


def add_user_email_address(data):
    fake_data = data[-1]
    new_email = faker.email()
    fake_data['email'] = new_email
    fake_data['emails'].append(
        {
            'id': 11,
            'created': '2019-02-13 09:42:37.888346+00:00',
            'modified': '2019-02-13 09:42:37.888929+00:00',
            'email': new_email,
            'verif_key': 'bf2da24f242eb9c0d82813f4f67755f59290f426',
            'verified_at': '2019-02-13 09:42:37.888643+00:00',
            'is_primary': True,
            'type_email': 'P'
        }
    )
    fake_data['emails'][0]['is_primary'] = False
    return data, new_email


class MigrateUserTest(UserTestMixin, APITestCase):

    def setUp(self):
        self.create_super_user()

    @patch.object(mail_handler, 'send_mail')
    def test_user_migrate(self, mock_email):
        data = FAKE_DATA
        url = reverse('api:migrate')

        # DO ACTION
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        users = User.objects.all()
        self.assertEqual(users.count(), 3)
        self.assertFalse(mock_email.called)
        for user_data in FAKE_DATA:
            user = User.objects.get(email=user_data.get('email'))
            self.assertTrue(
                User.objects.get(email=user.email).check_password('.eeepdQA'))
            self.assertEqual(user.id.__str__(), user_data.get('uuid'))
            self.assertIsNotNone(authenticate(
                username=user.email,
                password='.eeepdQA'))

    @patch.object(mail_handler, 'send_mail')
    def test_user_migrate_update(self, mock_email):
        data = FAKE_DATA
        url = reverse('api:migrate')
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)
        self.client.post(url, data=data)

        # DO ACTION
        data.append(NEW_USER_FAKE)
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        users = User.objects.all()
        self.assertEqual(users.count(), 4)
        self.assertTrue(
            User.objects.get(email='amyfinch@example.com').check_password('.eeepdQA'))
        self.assertFalse(mock_email.called)
        self.assertIsNotNone(authenticate(
            username='amyfinch@example.com',
            password='.eeepdQA'))
        user = User.objects.get(email='jsonmoss@example.com')
        self.assertEqual(user.id.__str__(), NEW_USER_FAKE['uuid'])
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_active)

    @patch.object(mail_handler, 'send_mail')
    def test_user_migrate_wrong_data(self, mock_email):
        data = FAKE_DATA
        data[1]['emails'][0]['remote_host'] = ''
        data[1]['emails'][0]['email'] = 'ff...@example.com'
        data[1]['email'] = 'ff...@example.com'
        url = reverse('api:migrate')

        # DO ACTION
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(
            User.objects.filter(email=data[1]['email']).exists())
        user = User.objects.get(email=data[1]['email'])
        self.assertIsNotNone(authenticate(
            username=user.email,
            password='.eeepdQA'))

    @patch.object(mail_handler, 'send_mail')
    def test_user_migrate_update_new_email(self, mock_email):
        data = FAKE_DATA
        url = reverse('api:migrate')
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)
        self.client.post(url, data=data)

        # DO ACTION
        data.append(NEW_USER_FAKE)
        data, new_email = add_user_email_address(data)
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        users = User.objects.all()
        self.assertEqual(users.count(), 4)
        user = User.objects.get(id='03214e9c-1f6b-4b52-8080-c7b0103a5755')
        self.assertEqual(user.email, new_email)
