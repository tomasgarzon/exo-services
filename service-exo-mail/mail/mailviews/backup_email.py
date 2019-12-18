# app imports
from ..mails import BaseMailView


class BackupEmailMailView(BaseMailView):
    template_name = 'mails/backup_email.html'
    mandatory_mail_args = ['s3_file']
    optional_mail_args = []
    section = 'backup'
    subject = 'backup'

    def get_mock_data(self, optional=True):
        mock_data = {'s3_file': 'file.tar.gz'}
        return mock_data
