from django.conf import settings
from django.utils import timezone

from utils.xlsx import XlsxWrapper

from ..question import Question


class SurveyReportMixin:

    def create_results_tab(self, worksheet):
        # Headers of the spreesheet
        headers_fixed = [
            (0, 'Name'),
            (1, 'Email'),
            (2, 'Organization'),
            (3, 'Industry'),
            (4, 'Created'),
            (5, 'Total'),
        ]
        for pos, name in headers_fixed:
            worksheet.write(0, pos, name)

        pos += 1

        headers_sections = settings.SURVEY_CH_SECTION
        for section_code, section_name in headers_sections:
            worksheet.write(0, pos, section_name.__str__())
            pos += 1

        headers_questions = Question.objects.all().values_list('order', flat=True)
        for question_order in headers_questions:
            worksheet.write(0, pos, question_order)
            pos += 1

        row = 1

        # Data of the spreesheet
        for survey_filled in self.surveys_filled.all():
            # headers_fixed
            worksheet.write(row, 0, survey_filled.name)
            worksheet.write(row, 1, survey_filled.email)
            worksheet.write(row, 2, survey_filled.organization)
            worksheet.write(row, 3, survey_filled.industry.name if survey_filled.industry else '-')
            worksheet.write(row, 4, survey_filled.created.strftime('%Y-%m-%d %H:%M:%S'))
            worksheet.write(row, 5, survey_filled.total)

            column = 6

            # headers_sections
            for result in survey_filled.results.all():
                worksheet.write(row, column, result.score)
                column += 1

            # headers_questions
            for answer in survey_filled.answers.all().order_by('question__order'):
                worksheet.write(row, column, answer.value)
                column += 1

            row += 1

    def create_index_tab(self, worksheet):
        # Headers of the spreesheet
        headers = [
            (0, 'Order'),
            (1, 'Section'),
            (2, 'Question'),
            (3, 'Options'),
        ]

        for pos, name in headers:
            worksheet.write(0, pos, name)

        # Data of the spreesheet
        row = 1
        for question in Question.objects.all():
            worksheet.write(row, 0, question.order)
            worksheet.write(row, 1, question.get_section_display())
            worksheet.write(row, 2, question.name)

            column = 3

            for option in question.options.all():
                worksheet.write(row, column, option.value)
                column += 1

            row += 1

    def get_report_csv(self):
        date = timezone.now().strftime('%Y-%m-%d')
        wrapper = XlsxWrapper('{} - {}'.format(date, self.name))

        worksheet_results = wrapper.create_worksheet('Results')
        worksheet_index = wrapper.create_worksheet('Index')

        self.create_results_tab(worksheet_results)
        self.create_index_tab(worksheet_index)

        wrapper.close()

        return wrapper
