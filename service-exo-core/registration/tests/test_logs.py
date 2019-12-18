from django.contrib.auth.models import Group
from django.test import tag

from django.test import TestCase
from consultant.faker_factories import FakeConsultantFactory
from test_utils.test_case_mixins import SuperUserTestMixin


from ..models import RegistrationProcess
from ..conf import settings


@tag('sequencial')
class TestProcessLog(SuperUserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()
        group = Group.objects.get(name=settings.REGISTRATION_GROUP_NAME)
        group.user_set.add(self.super_user)
        self.consultant = FakeConsultantFactory.create()

    def test_log_creation(self):

        process = RegistrationProcess._create_process(
            self.super_user,
            self.consultant.user,
        )

        self.assertEqual(process.logs.count(), 1)
        test_message = 'Log test message'
        process._store_log(
            text=test_message,
            status='A',
            display_status='accepted',
            related_object=process.current_step.content_object,
        )
        self.assertEqual(process.logs.count(), 2)
        log = process.logs.all().order_by('-id').first()
        self.assertIsNotNone(log.content_type_id)
        self.assertIsNotNone(log.object_id)
        self.assertIsNotNone(log.text)
        self.assertIsNotNone(log.status)
        self.assertIsNotNone(log.display_status)
        self.assertIsNotNone(log.date)
        self.assertTrue(log.display)

        process._store_log(
            text='Hidden log',
            status='A',
            display_status='accepted',
            display=False,
        )
        self.assertEqual(process.logs.count(), 3)
        self.assertTrue(test_message in '{}'.format(process.logs.all()[1]))
        self.assertEqual(
            '{}'.format(process.logs.all().order_by('-id')[0]),
            '',
        )
