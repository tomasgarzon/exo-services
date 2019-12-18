from django.contrib.auth import get_user_model

from survey.models import Question
from industry.models import Industry
from populate.populator.builder import Builder


User = get_user_model()


class SurveyFilledBuilder(Builder):

    def create_object(self):
        survey = self.data.get('survey')
        answers = self.parse_answers()
        industry = Industry.objects.get(name=self.data.get('industry'))
        return survey.fill(
            name=self.data.get('name'),
            organization=self.data.get('organization'),
            industry=industry,
            email=self.data.get('email'),
            answers=answers,
        )

    def parse_answers(self):
        answers = []
        for response in self.data.get('answers'):
            question = Question.objects.get(order=response.get('order'))
            option = question.options.get(order=response.get('option'))
            answers.append({
                'question': question,
                'option': option})
        return answers
