from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from mock import patch

from typeform_feedback.helpers import random_string
from typeform_feedback.models import (
    GenericTypeformFeedback,
    UserGenericTypeformFeedback,
)
from typeform_feedback.signals_define import new_user_typeform_response

from customer.faker_factories import FakeCustomerFactory
from test_utils.test_case_mixins import UserTestMixin


class TestTypeformSignals(UserTestMixin, TestCase):

    @patch('typeform.tasks.user_typeform_responses.NewUserTypeformResponseMailTask.apply_async')
    def test_send_notification_email_for_new_typeform_response(self, typeform_task):
        # PREPARE DATA
        customer = FakeCustomerFactory()
        self.create_user()

        generic_typeform = GenericTypeformFeedback.create_typeform(
            linked_object=customer,
            slug=random_string(),
            typeform_id=random_string(5),
        )
        user_typeform = UserGenericTypeformFeedback(
            feedback=generic_typeform,
            user=self.user,
        )
        user_typeform.save()

        # DO ACTION
        new_user_typeform_response.send(
            sender=UserGenericTypeformFeedback,
            uuid=user_typeform.uuid.__str__(),
            response={},
        )

        # ASSERTIONS
        self.assertTrue(typeform_task.called)

    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_send_notification_email_for_new_typeform_response_data_is_correct(self, send_mail_task):
        # PREPARE DATA
        customer = FakeCustomerFactory()
        self.create_user()

        generic_typeform = GenericTypeformFeedback.create_typeform(
            linked_object=customer,
            slug=random_string(),
            typeform_id=random_string(5),
        )
        user_typeform = UserGenericTypeformFeedback(
            feedback=generic_typeform,
            user=self.user,
        )
        user_typeform.save()

        # DO ACTION
        new_user_typeform_response.send(
            sender=UserGenericTypeformFeedback,
            uuid=user_typeform.uuid.__str__(),
            response={},
        )

        # ASSERTIONS
        self.assertTrue(send_mail_task.called)
        self.assertEqual(
            send_mail_task.call_args.kwargs.get('recipients'),
            settings.TYPEFORMFEEDBACK_NOTIFY_EMAILS_LIST,
        )
        self.assertEqual(
            send_mail_task.call_args.kwargs.get('public_url'),
            '{}{}'.format(
                settings.ROOT,
                reverse('typeform:typeform_feedback:validate', kwargs={'uuid': user_typeform.uuid.__str__()})
            )
        )
