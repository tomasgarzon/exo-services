from django.test import TestCase
from django.urls import reverse

from rest_framework import status

from consultant.faker_factories import FakeConsultantFactory
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin

from ..helpers import filters


class EcosystemFiltersTestCase(UserTestMixin, SuperUserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()

    def test_ecosystem_filters(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory(user=self.user)
        url = reverse('api:ecosystem:filters')

        outputs = [
            filters.get_industries_filter_data(),
            filters.get_attributes_filter_data(),
            filters.get_roles_filter_data(),
            filters.get_activities_filter_data(),
            filters.get_technologies_filter_data(),
            filters.get_languages_filter_data(),
            filters.get_location_filter_data(),
            filters.get_certifications_filter_data(),
        ]

        # DO ACTION
        self.client.login(
            username=consultant.user.username,
            password='123456'
        )
        response = self.client.get(url)

        # ASSERTS
        index = 0
        self.assertTrue(status.is_success(response.status_code))
        for data in response.json():
            self.assertEqual(
                data.get('title'),
                outputs[index].get('title'))
            self.assertEqual(
                data.get('queryparam'),
                outputs[index].get('queryparam'))
            self.assertEqual(
                data.get('multiselect'),
                outputs[index].get('multiselect'))
            self.assertEqual(
                len(data.get('items')),
                len(outputs[index].get('items')))
            index += 1

    def test_ecosystem_filters_with_staff_perms(self):
        # PREPARE DATA
        url = reverse('api:ecosystem:filters')

        outputs = [
            filters.get_industries_filter_data(),
            filters.get_attributes_filter_data(),
            filters.get_roles_filter_data(),
            filters.get_activities_filter_data(),
            filters.get_technologies_filter_data(),
            filters.get_languages_filter_data(),
            filters.get_location_filter_data(),
            filters.get_certifications_filter_data(),
            filters.get_staff_filter_data(),
        ]

        # DO ACTION
        self.client.login(
            username=self.super_user.username,
            password='123456'
        )
        response = self.client.get(url)

        # ASSERTS
        index = 0
        self.assertTrue(status.is_success(response.status_code))
        for data in response.json():
            self.assertEqual(
                data.get('title'),
                outputs[index].get('title'))
            self.assertEqual(
                data.get('queryparam'),
                outputs[index].get('queryparam'))
            self.assertEqual(
                data.get('multiselect'),
                outputs[index].get('multiselect'))
            self.assertEqual(
                len(data.get('items')),
                len(outputs[index].get('items')))
            index += 1
