from unittest.mock import patch
from actstream.models import following

from django.conf import settings

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from consultant.faker_factories import FakeConsultantFactory
from exo_accounts.test_mixins import FakeUserFactory
from forum.models import Post
from team.faker_factories import FakeTeamFactory
from keywords.faker_factories import FakeKeywordFactory
from test_utils import MagicMockMixin
from utils.faker_factory import faker
from test_utils.test_case_mixins import (
    SuperUserTestMixin,
    UserTestMixin,
    CertificationTestMixin,
)

from ..models import Circle


class CirclesApiTest(
        MagicMockMixin,
        CertificationTestMixin,
        UserTestMixin,
        SuperUserTestMixin,
        APITestCase):

    def setUp(self):
        self.create_superuser()
        self.consultant_1 = FakeConsultantFactory.create(
            user__is_active=True,
            activities=[
                settings.EXO_ACTIVITY_CH_ACTIVITY_CONSULTING,
                settings.EXO_ACTIVITY_CH_ACTIVITY_COACHING,
            ]
        )
        self.consultant_1.user.set_password('123456')
        self.consultant_1.user.save()

        self.certificate_consultant(
            email=self.consultant_1.user.email,
            _type='consultantrole-foundations',
            user_from=self.super_user,
        )

        for c in ['ecosystem', 'ambassadors', 'trainers']:
            circle = Circle.objects.get(slug=c)
            circle.add_user(self.consultant_1.user)

        self.consultant_2 = FakeConsultantFactory.create(
            user__is_active=True,
            activities=[settings.EXO_ACTIVITY_CH_ACTIVITY_CONSULTING])
        self.consultant_2.user.set_password('123456')
        self.consultant_2.user.save()

    def get_files_example(self, num=1):
        files = []
        for i in range(num):
            file = {
                'filestack_status': 'Stored',
                'filename': '{}.png'.format(faker.word()),
                'mimetype': 'image/png',
                'url': 'https://cdn.filestackcontent.com/{}'.format(faker.numerify()),
            }
            files.append(file)

        return files

    def get_tags_example(self, num=1):
        tags = []
        for i in range(num):
            keyword = FakeKeywordFactory.create()
            tag = {
                'pk': keyword.pk,
                'name': keyword.name,
            }
            tags.append(tag)
        return tags

    def assertExpectedKeys(self, data):
        expected_keys = [
            'canEdit', 'canPost', 'name', 'slug',
            'totalMembers', 'type', 'tags', 'userStatus',
        ]
        for key in expected_keys:
            self.assertTrue(key in data.keys())
            self.assertIsNotNone(data.get(key))

    def test_create_circle(self):
        # PREPARE DATA
        url = reverse('api:circles:circles-list')
        num_tags = 4
        data = {
            'name': faker.word(),
            'description': faker.text(),
            'tags': self.get_tags_example(num_tags),
            'image': self.get_files_example()[0],
        }

        # DO ACTION
        self.client.login(
            username=self.consultant_1.user.username,
            password='123456')
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertExpectedKeys(data)
        self.assertEqual(data.get('userStatus'), 'M')
        self.assertFalse(data.get('canLeave'))
        self.assertTrue('image' in data.keys())
        self.assertTrue('description' in data.keys())
        self.assertIsNone(data['certificationRequired'])

    def test_join_circle(self):
        # PREPARE DATA
        user_from = self.consultant_1.user
        circle = Circle.objects.create(
            name=faker.word(),
            description=faker.text(),
            created_by=user_from,
        )
        url = reverse('api:circles:circles-join', kwargs={'slug': circle.slug})

        # DO ACTION
        self.client.login(username=user_from.username, password='123456')
        response = self.client.post(url)

        # ASSERTS
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        data = response.json()

        self.assertExpectedKeys(data)
        self.assertFalse(data.get('canLeave'))
        self.assertEquals(data.get('userStatus'), 'M')

    def test_try_join_certified_circle(self):
        # PREPARE DATA
        user_from = self.consultant_2.user
        circle = Circle.objects.get(slug='trainers')
        url = reverse('api:circles:circles-join', kwargs={'slug': circle.slug})

        # DO ACTION
        self.client.login(username=user_from.username, password='123456')
        response = self.client.post(url)

        # ASSERTS
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_leave_circle(self):
        # PREPARE DATA
        user_from = self.consultant_1.user
        circle = Circle.objects.create(
            name=faker.word(),
            description=faker.text(),
            created_by=self.consultant_2.user,
        )
        circle.add_user(user_from)
        url = reverse('api:circles:circles-leave', kwargs={'slug': circle.slug})

        # DO ACTION
        self.client.login(username=user_from.username, password='123456')
        response = self.client.post(url)

        # ASSERTS
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertExpectedKeys(data)
        self.assertFalse(data.get('canLeave'))
        self.assertEquals(data.get('userStatus'), 'G')

    def test_try_creator_leave_circle(self):
        # PREPARE DATA
        user_from = self.consultant_1.user
        circle = Circle.objects.create(
            name=faker.word(),
            description=faker.text(),
            created_by=user_from,
        )
        circle.add_user(user_from)
        url = reverse('api:circles:circles-leave', kwargs={'slug': circle.slug})

        # DO ACTION
        self.client.login(username=user_from.username, password='123456')
        response = self.client.post(url)

        # ASSERTS
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_try_leave_certified_circle(self):
        # PREPARE DATA
        user_from = self.consultant_1.user
        circle = Circle.objects.get(slug='consultants')
        circle.add_user(user_from)
        url = reverse('api:circles:circles-leave', kwargs={'slug': circle.slug})

        # DO ACTION
        self.client.login(username=user_from.username, password='123456')
        response = self.client.post(url)

        # ASSERTS
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_circle(self):
        # PREPARE DATA
        user_from = self.consultant_1.user
        circle = Circle.objects.create(
            name=faker.word(),
            description=faker.text(),
            created_by=user_from,
        )
        url = reverse('api:circles:circles-detail', kwargs={'slug': circle.slug})
        num_tags = 4
        data = {
            'name': '{} EDITED'.format(circle.name),
            'description': faker.text(),
            'tags': self.get_tags_example(num_tags),
        }

        # DO ACTION
        self.client.login(username=user_from.username, password='123456')
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertExpectedKeys(data)
        self.assertTrue('image' in data.keys())
        self.assertTrue('description' in data.keys())
        self.assertTrue('EDITED' in data.get('name'))

    def test_update_circle_no_permissions(self):
        # PREPARE DATA
        user_from = self.consultant_1.user
        circle = Circle.objects.create(
            name=faker.word(),
            description=faker.text(),
            created_by=self.super_user,
        )
        url = reverse('api:circles:circles-detail', kwargs={'slug': circle.slug})
        num_tags = 4
        data = {
            'name': '{} EDITED'.format(circle.name),
            'description': faker.text(),
            'tags': self.get_tags_example(num_tags),
        }

        # DO ACTION
        self.client.login(username=user_from.username, password='123456')
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertEquals(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_circle_list_success(self):
        # PREPARE DATA
        url = reverse('api:circles:circles-list')

        for circle in Circle.objects.all():
            Post.objects.create_circle_post(
                user_from=self.super_user,
                circle=circle,
                title=' '.join(faker.words()),
                description=faker.text())
        Post.objects.create_announcement_post(
            user_from=self.super_user,
            title=' '.join(faker.words()),
            description=faker.text())
        Post.objects.create_project_team_post(
            title=''.join(faker.words()),
            user_from=self.super_user,
            team=FakeTeamFactory.create())
        open_circle = Circle.objects.create(
            name=faker.word(),
            description=faker.text(),
            created_by=self.consultant_1.user,
        )
        open_circle.add_user(self.consultant_1.user)
        consultant_circles = following(self.consultant_2.user, Circle)
        user_circles = following(self.consultant_1.user, Circle)

        # DO ACTION
        self.client.login(
            username=self.consultant_1.user.username, password='123456')
        response_1 = self.client.get(url)
        self.client.login(
            username=self.consultant_2.user.username, password='123456')
        response_2 = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response_1.status_code))
        data = response_1.json()
        self.assertEqual(data.get('count'), len(user_circles) + 2)
        self.assertTrue(status.is_success(response_2.status_code))
        data = response_2.json()
        self.assertEqual(data.get('count'), len(consultant_circles) + 1)

    def test_circle_list_with_deletion(self):
        # PREPARE DATA
        url = reverse('api:circles:circles-list')
        circles = Circle.objects.all()
        for circle in circles:
            Post.objects.create_circle_post(
                user_from=self.super_user,
                circle=circle,
                title=' '.join(faker.words()),
                description=faker.text())
            circle.add_user(self.consultant_1.user)
        deleted_circle = Circle.objects.first()
        deleted_circle.mark_as_removed()

        # DO ACTION
        self.client.login(
            username=self.consultant_1.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEquals(data.get('count'), len(circles) + 1)

    def test_circle_list_fail(self):
        # PREPARE DATA
        user = FakeUserFactory.create(is_active=True, password='123456')
        url = reverse('api:circles:circles-list')

        # DO ACTION
        self.client.login(username=user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    def test_circle_retrieve_subscribed(self):
        # PREPARE DATA
        circle = Circle.objects.get(slug='trainers')
        params = {'slug': circle.slug}
        url = reverse('api:circles:circles-detail', kwargs=params)

        # DO ACTION
        self.client.login(
            username=self.consultant_1.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertExpectedKeys(data)
        self.assertTrue(data.get('canPost'))

    def test_circle_retrieve_not_subscribed(self):
        # PREPARE DATA
        circle = Circle.objects.get(slug='trainers')
        params = {'slug': circle.slug}
        url = reverse('api:circles:circles-detail', kwargs=params)

        # DO ACTION
        self.client.login(
            username=self.consultant_2.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertExpectedKeys(data)
        self.assertEqual(data.get('userStatus'), 'G')

    def test_circle_retrieve_announcements(self):
        # PREPARE DATA
        params = {'slug': 'announcements'}
        url = reverse('api:circles:circles-detail', kwargs=params)

        # DO ACTION
        self.client.login(
            username=self.consultant_1.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertExpectedKeys(data)
        self.assertFalse(data.get('canPost'))

    @patch('forum.tasks.PostSendEmailCreatedTask.apply_async')
    def test_create_post_in_circle_success(self, post_emails_task_mock):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            user__is_active=True, user__password='123456')
        circle_slug = 'consultants'
        circle = Circle.objects.get(slug=circle_slug)
        circle.add_user(consultant.user)

        url = reverse('api:circles:circles-create', kwargs={'slug': circle_slug})
        keyword = FakeKeywordFactory.create()
        num_files = 2
        payload = {
            'title': ' '.join(faker.words()),
            'description': faker.text(),
            'tags': [
                {
                    'pk': keyword.pk,
                    'name': keyword.name,
                },
                {
                    'name': faker.word() + faker.numerify(),
                },
            ],
            'uploaded_files': self.get_files_example(num_files),
        }

        # DO ACTION
        self.client.login(username=consultant.user.username, password='123456')
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('pk'))
        post = Post.objects.get(pk=data.get('pk'))
        self.assertTrue(post.is_circle)
        self.assertIsNone(post.edited)
        self.assertTrue(post_emails_task_mock.called)
        self.assertEqual(post_emails_task_mock.call_count, 1)
        self.assertIsNotNone(
            self.get_mock_kwarg(post_emails_task_mock, 'eta'))
        self.assertEqual(len(post.uploaded_files), num_files)
        self.assertEqual(len(data.get('uploadedFiles')), num_files)

    def test_create_post_in_circle_fail(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            user__is_active=True, user__password='123456')
        circle_slug = 'investors'
        url = reverse('api:circles:circles-create', kwargs={'slug': circle_slug})
        keyword = FakeKeywordFactory.create()
        num_files = 2
        payload = {
            'title': ' '.join(faker.words()),
            'description': faker.text(),
            'tags': [
                {
                    'pk': keyword.pk,
                    'name': keyword.name,
                },
                {
                    'name': faker.word() + faker.numerify(),
                },
            ],
            'uploaded_files': self.get_files_example(num_files),
        }

        # DO ACTION
        self.client.login(username=consultant.user.username, password='123456')
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    @patch('forum.tasks.PostSendEmailCreatedTask.apply_async')
    def test_create_post_in_announcements_success(self, post_emails_task_mock):
        # PREPARE DATA
        circle_slug = 'announcements'
        url = reverse('api:circles:circles-create', kwargs={'slug': circle_slug})
        keyword = FakeKeywordFactory.create()
        user = self.consultant_1.user
        user.is_staff = True
        user.save()
        num_files = 2
        payload = {
            'title': ' '.join(faker.words()),
            'description': faker.text(),
            'tags': [
                {
                    'pk': keyword.pk,
                    'name': keyword.name,
                },
                {
                    'name': faker.word() + faker.numerify(),
                },
            ],
            'uploaded_files': self.get_files_example(num_files),
        }

        # DO ACTION
        self.client.login(username=self.consultant_1.user.username, password='123456')
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('pk'))
        post = Post.objects.get(pk=data.get('pk'))
        self.assertTrue(post.is_announcement)
        self.assertIsNone(post.edited)
        self.assertTrue(post_emails_task_mock.called)
        self.assertEqual(post_emails_task_mock.call_count, 1)
        self.assertIsNotNone(
            self.get_mock_kwarg(post_emails_task_mock, 'eta'))
        self.assertEqual(len(post.uploaded_files), num_files)
        self.assertEqual(len(data.get('uploadedFiles')), num_files)

    def test_create_post_in_announcements_fail(self):
        # PREPARE DATA
        circle_slug = 'announcements'
        url = reverse('api:circles:circles-create', kwargs={'slug': circle_slug})
        consultant = FakeConsultantFactory.create(
            user__is_active=True, user__password='123456')
        keyword = FakeKeywordFactory.create()
        num_files = 2
        payload = {
            'title': ' '.join(faker.words()),
            'description': faker.text(),
            'tags': [
                {
                    'pk': keyword.pk,
                    'name': keyword.name,
                },
                {
                    'name': faker.word() + faker.numerify(),
                },
            ],
            'uploaded_files': self.get_files_example(num_files),
        }

        # DO ACTION
        self.client.login(username=consultant.user.username, password='123456')
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    @patch('forum.tasks.PostSendEmailCreatedTask.apply_async')
    def test_update_post_files(self, post_emails_task_mock):
        # PREPARE DATA
        keyword = FakeKeywordFactory.create()
        num_files = 1
        files = self.get_files_example(num_files)
        consultant = FakeConsultantFactory.create(
            user__is_active=True, user__password='123456')
        circle_slug = 'consultants'
        circle = Circle.objects.get(slug=circle_slug)
        circle.add_user(consultant.user)
        data = {
            'title': ' '.join(faker.words()),
            'description': faker.text(),
            'tags': [
                {
                    'pk': keyword.pk,
                    'name': keyword.name,
                },
                {
                    'name': faker.word() + faker.numerify(),
                },
            ],
            'uploaded_files': files,
        }
        url = reverse('api:circles:circles-create', kwargs={'slug': circle_slug})
        self.client.login(username=consultant.user.username, password='123456')

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data.get('uploaded_files')), num_files)

        # PREPARE DATA
        num_files_new = 2
        new_files = self.get_files_example(num_files_new)
        data_put = {
            'title': data['title'],
            'description': data['description'],
            'tags': data['tags'],
            'uploaded_files': files + new_files,
        }

        # DO ACTION
        url = reverse('api:forum:post-detail', kwargs={'pk': response.data.get('pk')})
        response = self.client.put(url, data=data_put)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data.get('uploaded_files')), num_files + num_files_new)
