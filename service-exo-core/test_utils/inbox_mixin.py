from django.core import mail


class TestInboxMixin:

    def clear_inbox(self):
        mail.outbox = []

    def get_sent_mails(self):
        return mail.outbox

    def get_first_mail(self):
        return mail.outbox[0]

    def get_last_mail(self):
        return mail.outbox[-1]

    def get_inbox_length(self):
        return len(mail.outbox)

    def get_recipients(self, mail):
        return mail.recipients()

    def get_copy_list(self, mail):
        return mail.cc

    def get_inbox_recipients_email_list(self):
        emails_list = []
        inbox_mails = self.get_sent_mails()
        for email in inbox_mails:
            emails_list += self.get_recipients(email)
        return emails_list

    def is_email_in_recipients(self, email, sent_mail):
        return email in self.get_recipients(sent_mail)
