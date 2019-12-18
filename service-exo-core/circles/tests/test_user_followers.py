from django.urls import reverse
from django.conf import settings

from rest_framework import status

from consultant.faker_factories import FakeConsultantFactory
from consultant.models import Consultant
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from exo_activity.models import ExOActivity
from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from utils.faker_factory import faker

from ..models import Circle


class CircleFollowersAPITest(
        SuperUserTestMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        self.create_superuser()

    def test_circle_api(self):
        # PREPARE DATA
        circle = Circle.objects.first()
        user1 = FakeUserFactory.create(password='123456', is_active=True)
        user2 = FakeUserFactory.create(password='123456', is_active=True)

        circle.add_user(user1)
        circle.add_user(user2)

        url = reverse('api:circles:followers', kwargs={'slug': circle.slug})

        # DO ACTION
        self.client.login(
            username=user1.username,
            password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data['results']), 2)

    def test_circle_api_search(self):
        # PREPARE DATA
        circle = Circle.objects.first()
        user1 = FakeUserFactory.create(short_name='aa', password='123456', is_active=True)
        user2 = FakeUserFactory.create(short_name='bb', password='123456', is_active=True)

        circle.add_user(user1)
        circle.add_user(user2)

        url = reverse('api:circles:followers', kwargs={'slug': circle.slug})

        # DO ACTION
        self.client.login(
            username=user1.username,
            password='123456')
        response = self.client.get(url, data={'search': 'aa'})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data['results']), 1)

    def test_api_call_with_no_real_circles_raise_404(self):
        # PREPARE DATA
        circle_fake_name = faker.word()
        url = reverse('api:circles:followers', kwargs={'slug': circle_fake_name})
        self.client.login(
            username=self.super_user.username,
            password='123456')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(Circle.objects.filter(name=circle_fake_name).count(), 0)

    def test_api_call_user_no_circle_permission(self):
        # PREPARE DATA
        # PREPARE DATA
        circle = Circle.objects.first()
        user1 = FakeUserFactory()
        user2 = FakeUserFactory()
        circle.add_user(user1)

        url = reverse('api:circles:followers', kwargs={'slug': circle.slug})
        test_cases = [
            {'user': user1, 'status': status.HTTP_200_OK},
            {'user': user2, 'status': status.HTTP_403_FORBIDDEN},
        ]

        # DO ACTION
        for test_case in test_cases:
            self.client.login(
                username=test_case.get('user').username,
                password='123456')
            response = self.client.get(url)

            # ASSERTS
            self.assertTrue(response.status_code, test_case.get('status'))

    def test_api_announcements(self):
        # PREPARE DATA
        exo_consulting = ExOActivity.objects.get(
            code=settings.EXO_ACTIVITY_CH_ACTIVITY_CONSULTING)
        consultant = FakeConsultantFactory(user__is_active=True)
        exo_activity, _ = consultant.exo_profile.exo_activities.get_or_create(
            exo_activity=exo_consulting)
        exo_activity.enable()
        expected_followers = Consultant.objects.all().count()

        url = reverse(
            'api:circles:followers',
            kwargs={'slug': settings.CIRCLES_ANNOUNCEMENT_SLUG}
        )

        self.client.login(
            username=consultant.user.username,
            password=consultant.user.short_name)

        # ACTIONS
        response = self.client.get(url)

        # ASSERTIONS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(data.get('count'), expected_followers)

    def test_api_participant_questions(self):
        # PREPARE DATA
        exo_consulting = ExOActivity.objects.get(
            code=settings.EXO_ACTIVITY_CH_ACTIVITY_CONSULTING)
        consultant = FakeConsultantFactory(user__is_active=True)
        exo_activity, _ = consultant.exo_profile.exo_activities.get_or_create(
            exo_activity=exo_consulting)
        exo_activity.enable()
        expected_followers = Consultant.objects.filter_consulting_enabled().count()

        url = reverse(
            'api:circles:followers',
            kwargs={'slug': settings.CIRCLES_QUESTIONS_PROJECTS_SLUG}
        )

        self.client.login(
            username=consultant.user.username,
            password=consultant.user.short_name)

        # ACTIONS
        response = self.client.get(url)

        # ASSERTIONS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(data.get('count'), expected_followers)

    def test_circle_api_followers(self):
        # PREPARE DATA
        circle = Circle.objects.first()
        names = [
            ('Kevin', 'Kevin Allen'),
            ('Kevin', 'Kevin Alonso'),
            ('Nash', 'Nash Kevinal'),
        ]
        for short_name, full_name in names:
            user = FakeUserFactory.create(
                short_name=short_name,
                full_name=full_name,
                password='123456', is_active=True)
            circle.add_user(user)

        url = reverse('api:circles:followers', kwargs={'slug': circle.slug})

        # DO ACTION
        self.client.login(
            username=user.username,
            password='123456')
        response = self.client.get(url + '?search=kevinal')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data['results']), 2)
