import time

from datetime import datetime
from rest_framework import status
from unittest.mock import patch

from django.urls import reverse
from django.conf import settings

from circles.models import Circle
from consultant.faker_factories import FakeConsultantFactory
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from keywords.faker_factories import FakeKeywordFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from team.faker_factories import FakeTeamFactory
from test_utils.mock_mixins import MagicMockMixin
from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from utils.faker_factory import faker
from utils.dates import decrease_date

from ..models import Post


DATE_TIME = '2018/01/01 10:10:10 +0000'
DATE_TIME_MASK = '%Y/%m/%d %H:%M:%S %z'


class APIPostCrudTest(
        MagicMockMixin,
        UserTestMixin,
        SuperUserTestMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()
        self.user.is_staff = True
        self.user.save()

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

    @patch('forum.tasks.PostSendEmailCreatedTask.apply_async')
    def test_ask_the_ecosystem(self, post_emails_task_mock):
        # PREPARE DATA
        sprint = FakeSprintAutomatedFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        new_team = FakeTeamFactory.create(project=sprint.project_ptr)
        new_team.add_member(
            user_from=self.super_user,
            email=self.user.email,
            name=self.user.short_name,
        )
        keyword = FakeKeywordFactory.create()
        num_files = 3
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
            'uploaded_files': self.get_files_example(num_files),
        }

        url_params = {
            'team_pk': new_team.id,
            'project_pk': sprint.id,
        }
        url = reverse('api:forum:questions-team-list', kwargs=url_params)
        self.client.login(username=self.user.username, password='123456')

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertIsNotNone(response.data['pk'])
        post = Post.objects.get(pk=response.data['pk'])
        self.assertEqual(post.tags.count(), 2)
        self.assertTrue(post.is_project)
        self.assertTrue(post_emails_task_mock.called)
        self.assertEqual(post_emails_task_mock.call_count, 1)
        self.assertIsNotNone(
            self.get_mock_kwarg(post_emails_task_mock, 'eta'))
        self.assertEqual(len(post.uploaded_files), num_files)
        self.assertEqual(len(response.data.get('uploaded_files')), num_files)

    @patch('forum.tasks.PostSendEmailCreatedTask.apply_async')
    def test_create_circle_post(self, post_emails_task_mock):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            user__is_active=True, user__password='123456')
        circle = Circle.objects.first()
        circle.add_user(consultant.user)
        keyword = FakeKeywordFactory.create()
        num_files = 4
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
            'uploaded_files': self.get_files_example(num_files),
        }
        url = reverse('api:circles:circles-create', kwargs={'slug': circle.slug})

        # DO ACTION
        self.client.login(username=consultant.user.username, password='123456')
        response = self.client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data.get('uploaded_files')), num_files)

    def test_update_post(self):
        # PREPARE DATA
        post = Post.objects.create_announcement_post(
            user_from=self.user,
            title=' '.join(faker.words()),
            description=faker.text(),
        )
        url = reverse('api:forum:post-detail', kwargs={'pk': post.pk})
        self.client.login(username=self.user.username, password='123456')
        keyword = FakeKeywordFactory.create()

        # DO ACTION
        data = {
            'title': ' '.join(faker.words()),
            'description': faker.text(),
            'tags': [
                {
                    'pk': keyword.pk,
                    'name': keyword.name,
                },
                {
                    'name': faker.word(),
                },
            ],
            'uploaded_files': self.get_files_example(),
        }
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        post.refresh_from_db()
        self.assertEqual(post.title, data['title'])
        self.assertEqual(post.description, data['description'])
        self.assertEqual(post.tags.count(), 2)
        self.assertEqual(len(response.data.get('uploaded_files')), 1)

    def test_delete_post(self):
        # PREPARE DATA
        post = Post.objects.create_announcement_post(
            user_from=self.user,
            title=' '.join(faker.words()),
            description=faker.text(),
        )

        url = reverse('api:forum:post-detail', kwargs={'pk': post.pk})
        url_slug = reverse('api:forum:post-slug-detail', kwargs={'slug': post.slug})
        self.client.login(username=self.user.username, password='123456')
        keyword = FakeKeywordFactory.create()

        # DO ACTION
        data = {
            'title': ' '.join(faker.words()),
            'description': faker.text(),
            'tags': [
                {
                    'pk': keyword.pk,
                    'name': keyword.name,
                },
                {
                    'name': faker.word(),
                },
            ]
        }
        response = self.client.delete(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        with self.assertRaises(Post.DoesNotExist):
            post.refresh_from_db()
        self.assertEqual(Post.all_objects.filter(pk=post.pk).count(), 1)
        self.assertTrue(Post.all_objects.filter_by_status_removed().exists())

        # DO ACTION
        response_pk = self.client.get(url)
        response_slug = self.client.get(url_slug)

        # ASSERTS
        self.assertTrue(response_pk.status_code, status.HTTP_410_GONE)
        self.assertTrue(response_slug.status_code, status.HTTP_410_GONE)

    def test_retrieve_post_user_not_in_circle(self):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        post = Post.objects.create_circle_post(
            user_from=self.user,
            circle=self.circle,
            title=' '.join(faker.words()),
            description=faker.text())

        other_user = FakeUserFactory.create(is_active=True)
        other_user.set_password('123456')
        other_user.save()
        url = reverse('api:forum:post-slug-detail', kwargs={'slug': post.slug})

        self.client.login(
            username=other_user.username, password='123456')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_post_when_have_replies(self):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        post = Post.objects.create_circle_post(
            user_from=self.user,
            circle=self.circle,
            title=' '.join(faker.words()),
            description=faker.text())
        user = FakeUserFactory.create()
        user.hubs.create(hub=self.circle.hub)
        post.reply(user, faker.text())
        url = reverse('api:forum:post-detail', kwargs={'pk': post.pk})
        keyword = FakeKeywordFactory.create()

        # DO ACTION
        data = {
            'title': ' '.join(faker.words()),
            'description': faker.text(),
            'tags': [
                {
                    'pk': keyword.pk,
                    'name': keyword.name,
                },
                {
                    'name': faker.word(),
                },
            ]
        }
        self.client.login(username=self.user.username, password='123456')
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        post.refresh_from_db()
        self.assertTrue(
            post.can_update_or_remove(self.user, raise_exceptions=False))
        self.assertEqual(post.title, data['title'])

    def test_delete_post_when_have_replies(self):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        post = Post.objects.create_circle_post(
            user_from=self.user,
            circle=self.circle,
            title=' '.join(faker.words()),
            description=faker.text())
        user = FakeUserFactory.create()
        user.hubs.create(hub=self.circle.hub)
        post.reply(user, faker.text())
        url = reverse('api:forum:post-detail', kwargs={'pk': post.pk})
        keyword = FakeKeywordFactory.create()

        # DO ACTION
        data = {
            'title': ' '.join(faker.words()),
            'description': faker.text(),
            'tags': [
                {
                    'pk': keyword.pk,
                    'name': keyword.name,
                },
                {
                    'name': faker.word(),
                },
            ]
        }
        self.client.login(username=self.user.username, password='123456')
        self.client.delete(url, data=data)

        # ASSERTS
        self.assertTrue(
            post.can_update_or_remove(self.user, raise_exceptions=False))
        post = Post.all_objects.get(pk=post.pk)
        self.assertTrue(post.is_removed)

    def _assert_update_is_ok(self, post, response, data):
        self.assertTrue(status.is_success(response.status_code))
        post.refresh_from_db()
        self.assertEqual(post.title, data['title'])
        self.assertEqual(post.description, data['description'])
        self.assertEqual(post.tags.count(), 2)

    def test_update_question_by_user(self):
        # PREPARE DATA
        sprint = FakeSprintAutomatedFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        new_team = FakeTeamFactory.create(project=sprint.project_ptr)
        new_team.add_member(
            user_from=self.super_user,
            email=self.user.email,
            name=self.user.short_name,
        )
        post = Post.objects.create_project_team_post(
            user_from=self.super_user,
            team=new_team,
            title=' '.join(faker.words()),
            description=faker.text(),
        )
        keyword = FakeKeywordFactory.create()

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        url = reverse('api:forum:post-detail', kwargs={'pk': post.pk})
        data = {
            'title': ' '.join(faker.words()),
            'description': faker.text(),
            'tags': [
                {
                    'pk': keyword.pk,
                    'name': keyword.name,
                },
                {
                    'name': faker.word(),
                },
            ]
        }
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    def test_update_post_immediately_created(self):
        # PREPARE DATA
        post = Post.objects.create_announcement_post(
            user_from=self.user,
            title=' '.join(faker.words()),
            description=faker.text(),
        )

        # DO ACTION
        post.action_update(self.user)

        # ASSERTS
        time.sleep(1)
        self.assertIsNone(post.edited)

    @patch(
        'django.utils.timezone.now',
        return_value=datetime.strptime(DATE_TIME, DATE_TIME_MASK))
    def test_update_post_1_hour_after_created(self, mock):
        # PREPARE DATA
        post = Post.objects.create_announcement_post(
            user_from=self.user,
            title=' '.join(faker.words()),
            description=faker.text(),
        )

        # DO ACTION
        post.action_update(self.user)
        datetime_updated = decrease_date(seconds=3600)
        edit_action = post.action_object_actions.filter(
            verb=settings.FORUM_ACTION_EDIT_POST).first()
        edit_action.timestamp = datetime_updated
        edit_action.save()

        # ASSERTS
        self.assertIsNotNone(post.edited)
        self.assertEqual(edit_action.timestamp, datetime_updated)

    @patch(
        'django.utils.timezone.now',
        return_value=datetime.strptime(DATE_TIME, DATE_TIME_MASK))
    def test_update_post_before_post_delay_is_not_edited(self, mock):
        # PREPARE DATA
        post = Post.objects.create_announcement_post(
            user_from=self.user,
            title=' '.join(faker.words()),
            description=faker.text(),
        )

        # DO ACTION
        post.action_update(self.user)
        edit_action = post.action_object_actions.filter(
            verb=settings.FORUM_ACTION_EDIT_POST).first()
        is_not_edited_timelapse = settings.FORUM_NEW_POST_DELAY - 10
        edit_action.timestamp = decrease_date(seconds=is_not_edited_timelapse)
        edit_action.save()

        # ASSERTIONS
        self.assertIsNone(post.edited)

    @patch(
        'django.utils.timezone.now',
        return_value=datetime.strptime(DATE_TIME, DATE_TIME_MASK))
    def test_update_post_several_times_updates_edited_property(self, mock):
        # PREPARE DATA
        post = Post.objects.create_announcement_post(
            user_from=self.user,
            title=' '.join(faker.words()),
            description=faker.text(),
        )

        post.action_update(self.user)
        edit_action = post.action_object_actions.filter(
            verb=settings.FORUM_ACTION_EDIT_POST).first()
        edit_action.timestamp = decrease_date(seconds=settings.FORUM_NEW_POST_DELAY * 3)
        edit_action.save()

        # DO ACTION
        post.action_update(self.super_user)
        datetime_updated = decrease_date(seconds=settings.FORUM_NEW_POST_DELAY * 2)
        last_edit_action = post.action_object_actions.filter(
            verb=settings.FORUM_ACTION_EDIT_POST).first()
        last_edit_action.timestamp = datetime_updated
        last_edit_action.save()

        # ASSERTS
        self.assertEqual(
            last_edit_action.timestamp.time(),
            post.edited.timestamp.time())
