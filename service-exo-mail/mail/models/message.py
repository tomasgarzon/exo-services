import datetime
import io
import pickle

from django.db import models

from model_utils.models import TimeStampedModel

from ..manager import MessageManager
from ..storage import get_storage


class Message(TimeStampedModel):
    subject = models.CharField(max_length=200, db_index=True)
    body = models.TextField()
    from_email = models.CharField(max_length=200, db_index=True)
    reply_to = models.CharField(max_length=200)
    to_email = models.TextField()
    cc = models.TextField()
    bcc = models.TextField()
    message = models.CharField(max_length=200)
    category = models.CharField(max_length=200, default='')

    objects = MessageManager()

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return '[{}] {} ({})'.format(
            self.subject,
            self.created.strftime('%Y-%m-%dT%H:%M:%S'),
            self.to_email)

    @property
    def email(self):
        st = get_storage()
        file_content = st.read_file(self.message)
        return pickle.loads(file_content)

    @email.setter
    def email(self, message):
        now = datetime.datetime.now()
        timestamp = '{}{}'.format(
            now.strftime('%Y-%m-%dT%H:%M:%S'),
            ('-%02d' % now.microsecond),
        )
        contents = io.BytesIO(pickle.dumps(message, 0))
        st = get_storage()
        self.message = st.write_file(contents, timestamp)

    @property
    def to_addresses(self):
        return self.to_email

    @property
    def to_addresses_as_list(self):
        return self.to_addresses.split(',')

    @property
    def history(self):
        return self.log.order_by('-created')

    @property
    def status(self):
        if self.history.first():
            return self.history.first().get_action_display()
        else:
            return 'N/A'
