from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Question


class QuestionAPITest(APITestCase):

    def test_get_questions(self):
        # PREPARE DATA
        url = reverse('api:question-list')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            Question.objects.count(),
            len(response.data))
        data = response.json()
        for question_data in data:
            question = Question.objects.get(pk=question_data['pk'])
            self.assertEqual(question.name, question_data['name'])

    def test_get_questions_es(self):
        # PREPARE DATA
        url = reverse('api:question-list')

        # DO ACTION
        response = self.client.get(url, data={'lang': 'es'})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            Question.objects.count(),
            len(response.data))
        data = response.json()
        for question_data in data:
            question = Question.objects.get(pk=question_data['pk'])
            self.assertEqual(question.name_es, question_data['name'])
