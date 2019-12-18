from django.core.management.base import BaseCommand

from ...models import SurveyFilled


def calculate_new_version():
    for survey in SurveyFilled.objects.all():
        answers = []
        for answer in survey.answers.all():
            value = {
                'question': answer.question,
                'option': answer.option_selected}
            answers.append(value)
        if answers:
            survey._fill_answers(answers)


class Command(BaseCommand):
    help = 'Update ExQ Score'

    def handle(self, *args, **kwargs):
        calculate_new_version()
        self.stdout.write(self.style.SUCCESS('ExQ Updated successfully'))
