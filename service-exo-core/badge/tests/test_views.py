from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.utils.dateparse import parse_date

from rest_framework import status

from test_utils.test_case_mixins import SuperUserTestMixin, UserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from utils.faker_factory import faker

from ..faker_factories import FakeBadgeFactory, FakeUserBadgeFactory, FakeUserBadgeItemFactory
from ..models import UserBadge, UserBadgeItem


class UserBadgeViewsTestCase(SuperUserTestMixin, UserTestMixin, TestCase):

    def setUp(self):
        self.create_superuser()
        self.create_user()
        self.consultant = FakeConsultantFactory.create(
            user=self.user,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE)
        self.client.login(username=self.super_user.username, password='123456')

    def test_user_badge_activity_add_view_twice_request(self):
        # PREPARE DATA
        badge = FakeBadgeFactory.create(code=settings.BADGE_CODE_CONTENT_CREATOR)
        url = reverse('tools:badge:add-activity-job')
        data = {
            'email': self.user.email,
            'badge': badge.pk,
            'comment': faker.text(),
        }

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_redirect(response.status_code))
        self.assertTrue(self.user.get_badges(code=badge.code).exists())
        self.assertEqual(self.user.get_badges(code=badge.code).first().num, 1)

        # DO ACTION AGAIN
        self.client.post(url, data=data)

        # ASSERTS
        self.assertEqual(self.user.get_badges(code=badge.code).first().num, 1)

        # ASSERTS LOGS
        user_badge = self.user.get_badges(code=badge.code).first()
        self.assertEqual(
            user_badge
            .get_logs(verb=settings.BADGE_ACTION_LOG_CREATE)
            .filter(description=data.get('comment'))
            .count(), 1
        )
        self.assertEqual(
            user_badge
            .get_logs(verb=settings.BADGE_ACTION_LOG_UPDATE)
            .filter(description=data.get('comment'))
            .count(), 1
        )

    def test_user_badge_job_update_item_view(self):
        # PREPARE DATA
        user_badge_item = FakeUserBadgeItemFactory.create()
        url = reverse('tools:badge:update-job-item', kwargs={'pk': user_badge_item.pk})
        data = {
            'name': faker.name(),
            'date': faker.date(),
        }

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_redirect(response.status_code))
        user_badge_item.refresh_from_db()
        self.assertEqual(user_badge_item.name, data.get('name'))
        self.assertEqual(user_badge_item.date, parse_date(data.get('date')))

    def test_user_badge_item_delete_view(self):
        # PREPARE DATA
        user_badge_item = FakeUserBadgeItemFactory.create()
        url = reverse('tools:badge:delete-item', kwargs={'pk': user_badge_item.pk})

        # DO ACTION
        response = self.client.delete(url)

        # ASSERTS
        self.assertTrue(status.is_redirect(response.status_code))
        self.assertFalse(UserBadgeItem.objects.filter(pk=user_badge_item.pk).exists())

        # ASSERTS LOGS
        self.assertTrue(
            self.super_user.actor_actions
            .filter(
                verb=settings.BADGE_ACTION_LOG_DELETE,
                description='item {}'.format(user_badge_item.pk)
            )
            .exists()
        )

    def test_user_badge_delete_view(self):
        # PREPARE DATA
        user_badge = FakeUserBadgeFactory.create()
        url = reverse('tools:badge:delete', kwargs={'pk': user_badge.pk})

        # DO ACTION
        response = self.client.delete(url)

        # ASSERTS
        self.assertTrue(status.is_redirect(response.status_code))
        self.assertFalse(UserBadge.objects.filter(pk=user_badge.pk).exists())

        # ASSERTS LOGS
        self.assertTrue(
            self.super_user.actor_actions
            .filter(
                verb=settings.BADGE_ACTION_LOG_DELETE,
                description=user_badge.pk
            )
            .exists()
        )
