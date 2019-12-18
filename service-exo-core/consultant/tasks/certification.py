from django.utils import timezone
from django.conf import settings

from celery import Task

from utils.mail import handlers
from utils.xlsx import XlsxWrapper

from ..search.helpers import get_filtered_data
from ..models import Consultant


class CertificationReportTask(Task):
    name = 'CertificationtReportTask'
    ignore_results = True

    def set_report_columns(self, worksheet):

        columns = [
            ('A1', 'email'),
            ('B1', 'got certified L1'),
            ('C1', 'L2 payment date'),
            ('D1', 'L2 coupon used'),
            ('E1', 'L2 amount paid'),
            ('F1', 'L2 issued date'),
            ('G1', 'FT payment date'),
            ('H1', 'FT coupon used'),
            ('I1', 'FT amount paid'),
            ('J1', 'FT issued date'),
            ('K1', 'L3 payment date'),
            ('L1', 'L3 coupon used'),
            ('M1', 'L3 amount paid'),
            ('N1', 'L3 Issued date'),
        ]

        for pos, name in columns:
            worksheet.write(pos, name)

    def write_certification_status(self, consultant, worksheet, row, start, level, roles):
        certification = consultant.user.certification_request.filter(certification__level=level).first()
        if certification:
            if certification.status == 'A':
                worksheet.write(row, start, certification.modified.strftime('%d/%m/%Y'))
                worksheet.write(row, start + 2, certification.price)
            if certification.coupon:
                worksheet.write(row, start + 1, certification.coupon.__str__())
        consultant_role = consultant.consultant_roles.filter(certification_role__code__in=roles).first()
        if consultant_role:
            worksheet.write(row, start + 3, consultant_role.created.strftime('%d/%m/%Y'))

    def set_report_content(self, worksheet, queryset):
        row = 1
        consultants = Consultant.objects.all()

        role_f = settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS
        role_c = settings.EXO_ROLE_CODE_CERTIFICATION_CONSULTANT
        role_h = settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH
        role_t = settings.EXO_ROLE_CODE_CERTIFICATION_TRAINER
        level_2 = settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2
        level_2_ft = settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2A
        level_3 = settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_3

        for item in consultants:
            worksheet.write(row, 0, item.user.email)
            foundations = item.consultant_roles.filter(certification_role__code=role_f)
            if foundations.exists():
                worksheet.write(row, 1, foundations.first().created.strftime('%d/%m/%Y'))
            self.write_certification_status(
                item, worksheet, row, start=2,
                level=level_2,
                roles=[role_c])
            self.write_certification_status(
                item, worksheet, row, start=6,
                level=level_2_ft,
                roles=[role_c])
            self.write_certification_status(
                item, worksheet, row, start=10,
                level=level_3,
                roles=[role_h, role_t])
            row += 1

    def get_report_file(self, queryset):
        wrapper = XlsxWrapper('certification-report.csv')
        worksheet = wrapper.create_worksheet('Certification')

        self.set_report_columns(worksheet)
        self.set_report_content(worksheet, queryset)

        wrapper.close()

        date = timezone.now().strftime('%Y_%m_%d__%H_%M_%S')
        filename = 'certification-report-{}.xlsx'.format(date)

        return (filename, wrapper.read())

    def run(self, *args, **kwargs):
        email_recipient = kwargs.get('email_recipient')
        queryparam = kwargs.get('queryparam')
        order_by = kwargs.get('order_by')
        email_name = 'basic_email'

        queryset = get_filtered_data(
            Consultant.objects.all(),
            queryparam,
            order_by
        )

        date = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        file = self.get_report_file(queryset)

        kwargs = {
            'mail_title': 'Certification report',
            'mail_content': 'Date - {}'.format(date),
            'attachments': [file],
            'attachments_parsed': True,
        }

        handlers.mail_handler.send_mail(
            email_name,
            recipients=[email_recipient],
            **kwargs)
