from django.conf import settings
from django.test import TestCase, override_settings

import uuid
import requests_mock
import re
from unittest import mock

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker
from utils import remote_user

from .. import models
from ..faker_factories import FakeProjectFactory
from .test_mixin import ProjectTestMixin, request_mock_account


@override_settings(EXOLEVER_HOST='http://localhost')
class RemoteUserAPITest(
        UserTestMixin,
        ProjectTestMixin,
        TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        cls.project = FakeProjectFactory.create(created_by=cls.super_user)

    def setUp(self):
        super().setUp()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_create_remote_participants(self, mock_request):
        self.init_mock(mock_request)

        participant = self.project.project_roles.get(
            code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT)
        users = []
        for _ in range(5):
            user = models.UserProjectRole.objects.create_participant(**{
                'project': self.project,
                'created_by': self.project.created_by,
                'project_role': participant,
                'name': faker.name(),
                'email': faker.email()
            }).user
            users.append(user)
        user_already_created = users[-1]
        same_uuid = [_.uuid.__str__() for _ in users[:-1]]
        other_uuid = uuid.uuid4().__str__()

        def json_callback(request, context):
            # simulate user already created with another uuid
            if request.json()['uuid'] == user_already_created.uuid.__str__():
                return {'uuid': other_uuid, 'created': False}
            data = request.json()
            data['created'] = True
            return data

        handler = mock_request.register_uri(
            'POST',
            re.compile(
                remote_user.URL_CREATE_USER.format(
                    settings.EXOLEVER_HOST)),
            json=json_callback,
            status_code=201)

        # DO ACTION
        users_created = self.project._create_participants(self.project.created_by)

        # ASSERTS
        self.assertEqual(handler.call_count, 5)
        self.assertEqual(models.Participant.objects.count(), 0)
        self.assertEqual(len(users_created), 4)
        user_already_created.refresh_from_db()
        self.assertEqual(
            user_already_created.uuid.__str__(),
            other_uuid)
        for index, user in enumerate(users[:-1]):
            user.refresh_from_db()
            self.assertEqual(user.uuid.__str__(), same_uuid[index])

    @requests_mock.Mocker()
    def test_create_remote_existing_participants(self, mock_request):
        self.init_mock(mock_request)

        participant = self.project.project_roles.get(
            code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT)
        email = faker.email()
        user_previous = self.get_user()
        models.UserProjectRole.objects.create_participant(**{
            'project': self.project,
            'created_by': self.project.created_by,
            'project_role': participant,
            'name': faker.name(),
            'email': email,
        })

        def json_callback(request, context):
            # simulate user already created with another uuid
            if request.json()['email'] == email:
                return {'uuid': user_previous.uuid.__str__(), 'created': False}
            data = request.json()
            data['created'] = True
            return data

        handler = mock_request.register_uri(
            'POST',
            re.compile(
                remote_user.URL_CREATE_USER.format(
                    settings.EXOLEVER_HOST)),
            json=json_callback,
            status_code=201)

        # DO ACTION
        with mock.patch(
                'project.models.Project.check_remote_user',
                return_value=({'uuid': user_previous.uuid.__str__()}, True)):
            users_created = self.project._create_participants(
                self.project.created_by)

        # ASSERTS
        self.assertEqual(handler.call_count, 0)
        self.assertEqual(models.Participant.objects.count(), 0)
        self.assertEqual(len(users_created), 0)
