import os
import json

from django.core.management.base import BaseCommand

from ...models import Question, Option


class Command(BaseCommand):
    help = 'Create questions for surveys'
    FILE_PATH = 'questions.json'

    def read_data(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        filename = '{}/{}'.format(BASE_DIR, self.FILE_PATH)
        with open(filename, 'r') as f:
            content = f.read()
            return json.loads(content)

    def get_questions(self, data):
        questions = []
        for index, question in enumerate(data.get('data').get('questions')):
            value = {
                'name': question.get('value'),
                'section': question.get('key'),
                'order': index,
                'options': []
            }
            for index2, option in enumerate(question.get('options')):
                value_option = {
                    'value': option.get('value'),
                    'order': index2,
                    'score': option.get('score'),
                }
                value['options'].append(value_option)
            questions.append(value)
        return questions

    def create_questions(self, questions):
        Question.objects.all().delete()
        Option.objects.all().delete()
        for question in questions:
            options = question.pop('options')
            new_question = Question.objects.create(**question)
            for option in options:
                new_question.options.create(**option)

    def handle(self, *args, **kwargs):
        data = self.read_data()
        questions = self.get_questions(data)
        self.create_questions(questions)
        self.stdout.write(self.style.SUCCESS('Questions created successfully'))
