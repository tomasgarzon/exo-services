from django.utils import timezone

from celery import Task

from utils.mail import handlers
from utils.xlsx import XlsxWrapper

from ..search.helpers import get_filtered_data
from ..models import Consultant


class NetworkListReportTask(Task):
    name = 'NetworkListReportTask'
    ignore_results = True

    def set_report_columns(self, worksheet):
        styles = [
            ('A:A', 20),
            ('B:B', 40),
            ('C:C', 20),
            ('D:D', 40),
            ('E:E', 20),
            ('G:G', 20),
            ('H:H', 20),
        ]

        columns = [
            ('A1', 'Name'),
            ('B1', 'Email'),
            ('C1', 'Location'),
            ('D1', 'Languages'),
            ('E1', 'Status'),
            ('F1', 'ExO Certified'),
            ('G1', 'ExO Activities'),
            ('H1', 'ExO Roles'),
            ('I1', 'Total Projects'),
            ('J1', 'Joined'),
            ('K1', 'Last Activity'),
        ]

        for pos, value in styles:
            worksheet.set_column(pos, value)

        for pos, name in columns:
            worksheet.write(pos, name)

    def set_report_content(self, worksheet, queryset):
        row = 1

        for item in queryset:
            languages = [language.name for language in item.languages.all()]
            roles = {c_project_roles.exo_role.name for c_project_roles in item.roles.all()}
            activities = [
                '{} [{}]'.format(activity.exo_activity.name, activity.get_status_display())
                for activity in item.exo_profile.exo_activities.all()
            ]

            worksheet.write(row, 0, item.user.full_name)
            worksheet.write(row, 1, item.user.email)
            worksheet.write(row, 2, item.user.location)
            worksheet.write(row, 3, ', '.join(languages))
            worksheet.write(row, 4, item.status_detail)
            worksheet.write(row, 5, item.is_exo_certified)
            worksheet.write(row, 6, ', '.join(activities))
            worksheet.write(row, 7, ', '.join(list(roles)))
            worksheet.write(row, 8, item.projects.all().count())
            worksheet.write(row, 9, item.user.date_joined.strftime('%Y-%m-%d %H:%M:%S'))
            worksheet.write(row, 10, item.user.ecosystem_member.last_activity.strftime('%Y-%m-%d %H:%M:%S'))

            row += 1

    def get_report_file(self, queryset):
        wrapper = XlsxWrapper('network-report.csv')
        worksheet = wrapper.create_worksheet('Network')

        self.set_report_columns(worksheet)
        self.set_report_content(worksheet, queryset)

        wrapper.close()

        date = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        filename = 'network-report-{}.xlsx'.format(date)

        return (filename, wrapper.read())

    def run(self, *args, **kwargs):
        email_recipient = kwargs.get('email_recipient')
        queryparam = kwargs.get('queryparam')
        order_by = kwargs.get('order_by')
        email_name = 'basic_email'

        queryset = get_filtered_data(
            Consultant.all_objects.all(),
            queryparam,
            order_by
        )

        date = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        file = self.get_report_file(queryset)

        kwargs = {
            'mail_title': 'Network report',
            'mail_content': 'Date - {}'.format(date),
            'attachments': [file],
            'attachments_parsed': True,
        }

        handlers.mail_handler.send_mail(
            email_name,
            recipients=[email_recipient],
            **kwargs)


class ContractingDataListReportTask(Task):
    name = 'ContractingDataListReportTask'
    ignore_results = True

    def set_report_columns(self, worksheet):
        styles = [
            ('A:A', 20),
            ('B:B', 40),
            ('C:C', 20),
            ('D:D', 40),
            ('E:E', 20),
        ]

        columns = [
            ('A1', 'Email'),
            ('B1', 'Name'),
            ('C1', 'Address'),
            ('D1', 'Tax ID'),
            ('E1', 'Company Name'),
        ]

        for pos, value in styles:
            worksheet.set_column(pos, value)

        for pos, name in columns:
            worksheet.write(pos, name)

    def set_report_content(self, worksheet, queryset):
        row = 1

        for item in queryset:
            try:
                contracting_data = item.exo_profile.contracting_data
            except Exception:
                continue

            worksheet.write(row, 0, item.user.email)
            worksheet.write(row, 1, contracting_data.name or item.user.get_full_name())
            worksheet.write(row, 2, contracting_data.address)
            worksheet.write(row, 3, contracting_data.tax_id)
            worksheet.write(row, 4, contracting_data.company_name)

            row += 1

    def get_report_file(self, queryset):
        wrapper = XlsxWrapper('contracting-report.csv')
        worksheet = wrapper.create_worksheet('Network')

        self.set_report_columns(worksheet)
        self.set_report_content(worksheet, queryset)

        wrapper.close()

        date = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        filename = 'network-report-{}.xlsx'.format(date)

        return (filename, wrapper.read())

    def run(self, *args, **kwargs):
        email_recipient = kwargs.get('email_recipient')
        queryparam = kwargs.get('queryparam')
        order_by = kwargs.get('order_by')
        email_name = 'basic_email'

        queryset = get_filtered_data(
            Consultant.all_objects.all(),
            queryparam,
            order_by
        )

        date = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        file = self.get_report_file(queryset)

        kwargs = {
            'mail_title': 'Contracting Data report',
            'mail_content': 'Date - {}'.format(date),
            'attachments': [file],
            'attachments_parsed': True,
        }

        handlers.mail_handler.send_mail(
            email_name,
            recipients=[email_recipient],
            **kwargs)
