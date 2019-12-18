from django.utils.text import slugify
from django.contrib.auth.models import Group
from django.test import tag
from django.core import mail
from django.test import TestCase

from consultant.faker_factories import FakeConsultantFactory
from test_utils.test_case_mixins import SuperUserTestMixin

from ..models import registration_process_template
from ..models import RegistrationProcess, ProcessTemplateStepOption
from ..exceptions import ProcessStepException
from ..conf import settings


def construct_option(property_name, property_value, property_values=None):
    option = ProcessTemplateStepOption()
    option.name = property_name.replace('_', '')
    option.description = ''
    option.customizable = True
    option.pre_step = False
    option.post_step = True
    option.property_name = property_name
    option.property_value = property_value
    option.property_values = property_values
    option.save()
    return option


@tag('sequencial')
class TestRegistrationProcess(SuperUserTestMixin, TestCase):

    def setUp(self):
        self.create_superuser()
        group = Group.objects.get(name=settings.REGISTRATION_GROUP_NAME)
        group.user_set.add(self.super_user)
        self.consultant = FakeConsultantFactory.create()

    def _create_process(self, options, version):
        """
            Create a default RegistrationTemplate for test
        """
        template = registration_process_template.RegistrationProcessTemplate(
            name='Certification v1',
            version=version,
        )
        template.save()
        # ##
        # Create Certification Process using the Previous template
        # ##
        steps_names = ['Agreement', ]
        notification = registration_process_template.NotificationStep(
            email_ok='certification_step_accept',
            email_ko='certification_step_decline',
        )
        notification.save()
        step = registration_process_template.ProcessTemplateStep.objects.create(
            template=template,
            name=steps_names[0],
            code=slugify(steps_names[0]),
            action=settings.CONSULTANT_VALIDATION_AGREEMENT,
            email_tpl=notification,
        )
        for opt in options:
            step.options.add(opt)

        consultant = FakeConsultantFactory()

        # ##
        # Create the certification using this Template
        # ##
        process = RegistrationProcess.create_process(
            user_from=self.super_user,
            user=consultant.user,
            version=version,
        )

        return process

    def test_steps_options_property_true_false_none(self):
        """
            This test will check options than are defined for this status:
                - True
                - False
                - None
        """
        options = []
        options.append(construct_option(
            'test_property_true',
            True,
        ))
        options.append(construct_option(
            'test_property_false',
            False,
        ))

        tpl_version = 999

        process = self._create_process(
            version=tpl_version,
            options=options,
        )

        self.assertTrue(process.check_option(option='test_property_true'))
        self.assertFalse(process.check_option(option='test_property_false'))
        self.assertFalse(process.check_option(option='unexisting_property'))

    def test_steps_options_property_values(self):
        """
            This test will check options that are defined to match an element for
            an array of possible values
        """
        options = []
        options.append(
            construct_option(
                property_name='test_property_values_option',
                property_value=None,
                property_values=['a', 'b', 'c'],
            ),
        )
        tpl_version = 56421

        process = self._create_process(
            version=tpl_version,
            options=options,
        )

        # Check property evaluation
        with self.assertRaises(ProcessStepException):
            process.check_option(option='test_property_values_option')

        self.assertFalse(process.check_option(
            option='test_property_values_option',
            value='x',
        ))
        self.assertTrue(process.check_option(
            option='test_property_values_option',
            value='a',
        ))

    def test_step_option_send_user_email__true(self):
        options = []
        options.append(construct_option(
            settings.REGISTRATION_OPTION_SEND_USER_EMAIL,
            True,
        ))
        tpl_version = 999
        mail.outbox = []

        process = self._create_process(
            version=tpl_version,
            options=options,
        )

        self.assertTrue(
            process.check_option(option=settings.REGISTRATION_OPTION_SEND_USER_EMAIL),
        )
        self.assertTrue(process.current_step.content_object.is_sent)
        self.assertEqual(len(mail.outbox), 1)

    def test_step_option_send_user_email__false(self):
        options = []
        options.append(construct_option(
            settings.REGISTRATION_OPTION_SEND_USER_EMAIL,
            False,
        ))
        tpl_version = 9999
        mail.outbox = []

        process = self._create_process(
            version=tpl_version,
            options=options,
        )

        self.assertFalse(
            process.check_option(option=settings.REGISTRATION_OPTION_SEND_USER_EMAIL),
        )
        self.assertTrue(process.current_step.content_object.is_skipped)
        self.assertEqual(len(mail.outbox), 0)

    def test_step_option_send_user_email__none(self):
        options = []
        tpl_version = 99999
        mail.outbox = []

        process = self._create_process(
            version=tpl_version,
            options=options,
        )

        self.assertIsNone(
            process.check_option(option=settings.REGISTRATION_OPTION_SEND_USER_EMAIL),
        )
        self.assertTrue(process.current_step.content_object.is_sent)
        self.assertEqual(len(mail.outbox), 1)

    def test_log_display_option(self):

        options = []
        options.append(
            construct_option(
                property_name=settings.REGISTRATION_OPTION_PUBLIC_LOG_VIEW,
                property_value=None,
                property_values=settings.CONSULTANT_VALIDATION_STATUS_PUBLIC_LOG,
            ),
        )
        tpl_version = 32154

        process = self._create_process(
            version=tpl_version,
            options=options,
        )

        self.assertTrue(
            process.check_option(
                option=settings.REGISTRATION_OPTION_PUBLIC_LOG_VIEW,
                value=process.current_step.content_object.status,
            ),
        )
        self.assertEqual(process.logs.count(), 1)
        self.assertTrue(process.logs.first().display)

        # ##
        # Test not make status S visible for users
        # ##
        options = []
        options.append(
            construct_option(
                property_name=settings.REGISTRATION_OPTION_PUBLIC_LOG_VIEW,
                property_value=None,
                property_values=['_'],
            ),
        )
        tpl_version = 3215
        process = self._create_process(
            version=tpl_version,
            options=options,
        )

        self.assertFalse(
            process.check_option(
                option=settings.REGISTRATION_OPTION_PUBLIC_LOG_VIEW,
                value=process.current_step.content_object.status,
            ),
        )
        self.assertEqual(process.logs.count(), 1)
        self.assertFalse(process.logs.first().display)
