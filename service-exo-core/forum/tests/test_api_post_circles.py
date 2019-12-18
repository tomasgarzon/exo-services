from django.conf import settings

from rest_framework import status
from rest_framework.reverse import reverse

from circles.models import Circle
from consultant.faker_factories import FakeConsultantFactory
from exo_accounts.test_mixins import FakeUserFactory
from team.faker_factories import FakeTeamFactory
from forum.models import Post
from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import (
    UserTestMixin,
    SuperUserTestMixin,
    CertificationTestMixin,
)
from utils.dates import string_to_datetime

from utils.faker_factory import faker


class APIPostCirclesTest(
        UserTestMixin,
        SuperUserTestMixin,
        CertificationTestMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()

    def test_announcement_post_list(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            user__is_active=True, user__password='123456')
        for i in range(5):
            Post.objects.create_announcement_post(
                user_from=self.super_user,
                title=' '.join(faker.words()),
                description=faker.text())

        url = reverse('api:forum:circle-post-list', kwargs={'circle_slug': 'announcements'})
        all_announcements = Post.objects.filter_by__type(
            settings.FORUM_CH_ANNOUNCEMENT)
        search = all_announcements.first().title
        search_announcements = all_announcements.filter_by_search(search)

        # DO ACTIONS
        self.client.login(username=consultant.user.username, password='123456')
        response = self.client.get(url)
        response_search = self.client.get(url, data={'search': search})
        self.client.login(username=self.super_user.username, password='123456')
        response_su = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(status.is_success(response_search.status_code))
        self.assertTrue(status.is_success(response_su.status_code))
        data = response.json()
        data_search = response_search.json()
        self.assertEqual(data.get('count'), all_announcements.count())
        self.assertEqual(data_search.get('count'), search_announcements.count())

    def test_post_list_from_circle_without_permissions(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(user__is_active=True, user__password='123456')
        circle = Circle.objects.get(name=settings.CIRCLES_ECOSYSTEM_NAME)
        self.client.login(username=consultant.user.username, password='123456')

        for i in range(5):
            Post.objects.create_circle_post(
                user_from=self.super_user,
                circle=circle,
                title=' '.join(faker.words()),
                description=faker.text())

        url = reverse('api:forum:circle-post-list', kwargs={'circle_slug': circle.slug})

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # DO ACTION
        circle.add_user(consultant.user)
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    def test_post_list_from_circle_removed(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(user__is_active=True, user__password='123456')
        circle = Circle.objects.get(name=settings.CIRCLES_ECOSYSTEM_NAME)
        circle.add_user(consultant.user)
        self.client.login(username=consultant.user.username, password='123456')

        for i in range(5):
            Post.objects.create_circle_post(
                user_from=self.super_user,
                circle=circle,
                title=' '.join(faker.words()),
                description=faker.text())

        url = reverse('api:forum:circle-post-list', kwargs={'circle_slug': circle.slug})

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

        # DO ACTION
        circle.mark_as_removed()
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))
        self.assertEqual(response.status_code, status.HTTP_410_GONE)

    def test_question_from_project_post_list(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            user__is_active=True, user__password='123456')
        for i in range(5):
            Post.objects.create_project_team_post(
                title=''.join(faker.words()),
                user_from=self.super_user,
                team=FakeTeamFactory.create())

        url = reverse('api:forum:circle-post-list', kwargs={'circle_slug': 'participant-questions'})

        # DO ACTIONS
        self.client.login(username=consultant.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(data.get('count'), 5)

    def test_announcement_post_fail(self):
        # PREPARE DATA
        user = FakeUserFactory.create(is_active=True, password='123456')
        for i in range(30):
            Post.objects.create_announcement_post(
                user_from=self.super_user,
                title=' '.join(faker.words()),
                description=faker.text())
        url = reverse('api:forum:circle-post-list', kwargs={'circle_slug': 'announcements'})

        # DO ACTION
        self.client.login(username=user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_circle_post_list(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            user__is_active=True, user__password='123456')
        self.circle = Circle.objects.first()
        second_circle = Circle.objects.last()
        consultant.user.hubs.create(hub=self.circle.hub)
        consultant.user.hubs.create(hub=second_circle.hub)
        url_params = {'circle_slug': self.circle.slug}
        url = reverse('api:forum:circle-post-list', kwargs=url_params)

        for i in range(6):
            Post.objects.create_circle_post(
                circle=self.circle,
                user_from=consultant.user,
                title=' '.join(faker.words()),
                description=faker.text())

        for i in range(10):
            Post.objects.create_circle_post(
                circle=second_circle,
                user_from=consultant.user,
                title=' '.join(faker.words()),
                description=faker.text())

        all_posts = Post.objects.filter_by_circle(self.circle)
        search = all_posts.first().title
        search_posts = all_posts.filter_by_search(search)

        # DO ACTION
        self.client.login(username=consultant.user.username, password='123456')
        response = self.client.get(url)
        response_search = self.client.get(url, data={'search': search})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(status.is_success(response_search.status_code))
        data = response.json()
        data_search = response_search.json()
        self.assertEqual(data.get('count'), all_posts.count())
        self.assertEqual(data_search.get('count'), search_posts.count())

    def test_circle_post_list_fail(self):
        # PREPARE DATA
        user = FakeUserFactory.create(is_active=True, password='123456')
        self.circle = Circle.objects.first()
        url_params = {'circle_slug': self.circle.slug}
        url = reverse('api:forum:circle-post-list', kwargs=url_params)

        # DO ACTION
        self.client.login(username=user.username, password='123456')
        response = self.client.get(url, kwargs=url_params)

        # ASSERTS
        self.assertTrue(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_post(self):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        post = Post.objects.create_circle_post(
            circle=self.circle,
            user_from=self.user,
            title=' '.join(faker.words()),
            description=faker.text())
        user_read_only = FakeUserFactory(is_active=True, password='123456')
        url_slug = reverse('api:forum:post-slug-detail', kwargs={'slug': post.slug})
        url = reverse('api:forum:post-detail', kwargs={'pk': post.pk})

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)
        response_slug = self.client.get(url_slug)
        self.client.login(username=user_read_only.username, password='123456')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        data_slug = response_slug.json()
        self.assertEqual(post.pk, data_slug.get('pk'))
        self.assertEqual(post.pk, data.get('pk'))
        self.assertEqual(post.answers.count(), data.get('answers'))
        self.assertEqual(
            post.answers_unseen(self.user), data.get('answersUnseen'))
        self.assertIn('avgRating', data)
        self.assertEqual(
            post.can_update_or_remove(self.user), data.get('canEdit'))
        self.assertTrue(data.get('canReply'))
        self.assertEqual(
            post.created, string_to_datetime(data.get('created')))
        self.assertIsNotNone(data.get('createdBy'))
        self.assertIn('counterRating', data)
        self.assertEqual(post.description, data.get('description'))
        self.assertEqual(
            post.modified, string_to_datetime(data.get('modified')))
        self.assertEqual(
            post.has_seen(self.user), data.get('seen'))
        self.assertEqual(post.tags.count(), len(data.get('tags')))
        self.assertEqual(post.title, data.get('title'))
        self.assertEqual(
            len(post.uploaded_files), len(data.get('uploadedFiles')))
        self.assertEqual(
            post.url_project, data.get('urlProject', ''))
        self.assertIn('yourRating', data)

    def test_retrieve_post_answers(self):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        post = Post.objects.create_circle_post(
            circle=self.circle,
            user_from=self.user,
            title=' '.join(faker.words()),
            description=faker.text())
        user_1 = FakeUserFactory.create()
        user_1.hubs.create(hub=self.circle.hub)
        user_2 = FakeUserFactory.create()
        user_2.hubs.create(hub=self.circle.hub)
        post.reply(user_1, faker.text())
        post.reply(user_2, faker.text())
        post.reply(self.user, faker.text())
        post.reply(user_1, faker.text())
        url = reverse('api:forum:post-answers', kwargs={'pk': post.pk})

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(data.get('count'), 4)

    def test_get_post_answer_seen(self):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        post = Post.objects.create_circle_post(
            circle=self.circle,
            user_from=self.user,
            title=' '.join(faker.words()),
            description=faker.text())
        user_1 = FakeUserFactory.create()
        user_1.hubs.create(hub=self.circle.hub)
        user_2 = FakeUserFactory.create()
        user_2.hubs.create(hub=self.circle.hub)
        post.reply(user_1, faker.text())
        post.reply(user_2, faker.text())
        post.reply(user_1, faker.text())
        url = reverse('api:forum:post-answers', kwargs={'pk': post.pk})

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        unseen_response = self.client.get(url)
        seen_response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(unseen_response.status_code))
        data = unseen_response.json()
        for item in data.get('results', None):
            self.assertFalse(item.get('seen'))

        self.assertTrue(status.is_success(seen_response.status_code))
        data = seen_response.json()
        for item in data.get('results', None):
            self.assertTrue(item.get('seen'))

    def test_get_post_without_answers_seen(self):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        post = Post.objects.create_circle_post(
            circle=self.circle,
            user_from=self.user,
            title=' '.join(faker.words()),
            description=faker.text())
        user_1 = FakeUserFactory.create(password='123456')
        user_1.hubs.create(hub=self.circle.hub)
        url = reverse('api:forum:post-answers', kwargs={'pk': post.pk})

        # ASSERTS
        self.assertFalse(post.has_seen(user_1))

        # DO ACTION
        self.client.login(username=user_1.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(post.has_seen(user_1))

    def test_retrieve_post_legacy_compatibility(self):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        post = Post.objects.create_circle_post(
            circle=self.circle,
            user_from=self.user,
            title=' '.join(faker.words()),
            description=faker.text())

        url = reverse('api:forum:post-slug-legacy-details', kwargs={'slug': post.slug})

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data.get('circle_slug'), self.circle.slug)
        self.assertFalse(response.data.get('is_removed'))

        # PREPARE DATA
        announcement = Post.objects.create_announcement_post(
            user_from=self.super_user,
            title=' '.join(faker.words()),
            description=faker.text())
        announcement.mark_as_removed(self.super_user)
        url = reverse('api:forum:post-slug-legacy-details', kwargs={'slug': announcement.slug})

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data.get('circle_slug'), settings.CIRCLES_ANNOUNCEMENT_SLUG)
        self.assertTrue(response.data.get('is_removed'))

    def test_retrieve_project_post_success(self):
        # PREPARE DATA
        post = Post.objects.create_project_team_post(
            title=''.join(faker.words()),
            user_from=self.super_user,
            team=FakeTeamFactory.create())

        consultant = FakeConsultantFactory.create()
        self.certificate_consultant(
            email=consultant.user.email,
            _type='consultantrole-foundations',
            user_from=self.super_user,
        )
        user = consultant.user
        user.set_password('123456')
        user.save()

        url = reverse('api:forum:post-slug-detail', kwargs={'slug': post.slug})

        # DO ACTION
        self.client.login(username=user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
