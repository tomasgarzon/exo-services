from django.test import TestCase
from django.conf import settings

from utils.faker_factory import faker
from utils.test_mixin import UserTestMixin
from industry.models import Industry

from ..faker_factories.survey import FakeSurveyFactory
from ..faker_factories.survey_filled import FakeSurveyFilledFactory
from ..models import Question


class CalculateExQAPITest(UserTestMixin, TestCase):

    def setUp(self):
        self.create_user()

    def test_calculate_score(self):
        # PREPARE DATA
        survey = FakeSurveyFactory.create(created_by=self.user)

        # DO ACTION
        survey_filled = FakeSurveyFilledFactory.create(
            survey=survey)

        # ASSERTS
        total = survey_filled.total
        self.assertTrue(total >= 0 and total <= 100)

    def get_response_1(self):
        user_answers = [
            (1.25, 1.25, 1.25),
            (1.25, 2.5, 1.25),
            (2.5, 2.5, 2.5),
            (3, 3, 3),
            (0.5, 0.5, 2.5),
            (1.25, 1.25, 1.25),
            (1.25, 2.5, 1.25),
            (1.25, 0.5, 1.25),
            (1.25, 1.25, 1.25),
            (1.25, 1.25, 1.25),
            (1.25, 1.25, 1.25),
            (0.99,)
        ]
        avg_attribute = [
            1.25, 1.67, 2.50, 3.00, 1.17, 1.25,
            1.67, 1.00, 1.25, 1.25, 1.25, 0.99]
        final_exq = 41.41
        return user_answers, avg_attribute, final_exq

    def get_response_2(self):
        user_answers = [[3] * 3] * 11
        user_answers.append([1])
        avg_attribute = [3] * 11 + [1]
        final_exq = 100
        return user_answers, avg_attribute, final_exq

    def fill_data(self, user_answers):
        data = {
            'name': faker.word(),
            'organization': faker.word(),
            'email': faker.email(),
            'industry': Industry.objects.first(),
            'answers': []
        }

        for index, (section, _) in enumerate(settings.SURVEY_CH_SECTION):
            section_answers = user_answers[index]
            for index2, answer in enumerate(section_answers):
                question = Question.objects.filter(
                    section=section)[index2]
                option = question.options.get(score=answer)
                data['answers'].append({
                    'question': question,
                    'option': option})
        return data

    def test_calcualte_score(self):
        # PREPARE DATA
        survey = FakeSurveyFactory.create(created_by=self.user)
        user_answers, avg_attribute, final_exq = self.get_response_1()

        data = self.fill_data(user_answers)

        # DO ACTION
        survey.fill(**data)

        # ASSERTS
        survey_filled = survey.surveys_filled.first()

        self.assertEqual(survey_filled.total, final_exq)
        for index, result in enumerate(survey_filled.results.all()):
            self.assertEqual(
                result.score, avg_attribute[index])

    def test_calcualte_max_score(self):
        # PREPARE DATA
        survey = FakeSurveyFactory.create(created_by=self.user)

        user_answers, avg_attribute, final_exq = self.get_response_2()

        data = self.fill_data(user_answers)

        # DO ACTION
        survey.fill(**data)

        # ASSERTS
        survey_filled = survey.surveys_filled.first()

        self.assertEqual(survey_filled.total, final_exq)
        for index, result in enumerate(survey_filled.results.all()):
            self.assertEqual(
                result.score, avg_attribute[index])

    def test_update_score(self):
        # PREPARE DATA
        survey = FakeSurveyFactory.create(created_by=self.user)
        user_answers, avg_attribute, first_score = self.get_response_1()

        data = self.fill_data(user_answers)

        # DO ACTION
        survey.fill(**data)

        # ASSERTS
        survey_filled = survey.surveys_filled.first()

        self.assertEqual(survey_filled.total, first_score)
        for index, result in enumerate(survey_filled.results.all()):
            self.assertEqual(
                result.score, avg_attribute[index])

        # OTHER RESPONSES
        user_answers, avg_attribute, final_exq = self.get_response_2()

        data = self.fill_data(user_answers)

        # DO ACTION
        survey_filled._fill_answers(data['answers'])
        survey_filled.refresh_from_db()

        self.assertEqual(survey_filled.total, final_exq)
        for index, result in enumerate(survey_filled.results.all()):
            self.assertEqual(
                result.score, avg_attribute[index])
        self.assertEqual(
            survey_filled.result_logs.count(), 1)
        self.assertEqual(
            survey_filled.result_logs.first().score, first_score)
