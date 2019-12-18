from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Industry


class IndustryAPITest(APITestCase):

    def test_get_questions(self):
        # PREPARE DATA
        url = reverse('industry:list')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            Industry.objects.count(),
            len(response.data))
        data = response.json()
        for industry_data in data:
            industry = Industry.objects.get(pk=industry_data['pk'])
            self.assertEqual(industry.name, industry_data['name'])

    def test_get_questions_es(self):
        # PREPARE DATA
        url = reverse('industry:list')

        # DO ACTION
        response = self.client.get(url, data={'lang': 'es'})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            Industry.objects.count(),
            len(response.data))
        data = response.json()
        for industry_data in data:
            industry = Industry.objects.get(pk=industry_data['pk'])
            self.assertEqual(industry.name_es, industry_data['name'])
