import os
import json

from django.core.management.base import BaseCommand
from django.utils import translation

from ...models import Question


class Command(BaseCommand):
    help = 'Update questions for surveys'
    FILE_PATH_ES = 'questions_es.json'
    FILE_PATH_EN = 'questions.json'

    def read_data(self, file_path):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        filename = '{}/{}'.format(BASE_DIR, file_path)
        with open(filename, 'r') as f:
            content = f.read()
            return json.loads(content)

    def update_questions_en(self, data):
        translation.activate('en')
        for index, question_data in enumerate(data.get('data').get('questions')):
            question = Question.objects.get(order=index)
            question.name = question_data.get('value')
            question.save()
            for index2, option_data in enumerate(question_data.get('options')):
                option = question.options.get(order=index2)
                option.value = option_data.get('value')
                option.save()

    def update_questions(self, data):
        translation.activate('es')
        for question_data in data.get('data').get('questions'):
            question = Question.objects.get(order=question_data.get('order'))
            question.name = question_data.get('value')
            question.save()

            for option_data in question_data.get('options'):
                option = question.options.get(order=option_data.get('order'))
                option.value = option_data.get('value')
                option.save()

    def handle(self, *args, **kwargs):
        data_es = self.read_data(self.FILE_PATH_ES)
        data_en = self.read_data(self.FILE_PATH_EN)
        self.update_questions(data_es)
        self.update_questions_en(data_en)
        self.stdout.write(self.style.SUCCESS('Questions updated successfully'))
