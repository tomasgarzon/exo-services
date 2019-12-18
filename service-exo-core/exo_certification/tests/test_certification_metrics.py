from django.conf import settings
from django.test import TestCase

from mock import patch

from exo_role.models import CertificationRole

from utils.metric.metric_mixin import CustomAction
from relation.faker_factories import FakeConsultantRoleGroupFactory, FakeConsultantRoleFactory
from consultant.faker_factories import FakeConsultantFactory
from relation.signals_define import user_certified

from .test_mixins import ExOCertificationTestMixin
from ..faker_factories import FakeCertificationRequestFactory
from ..models import CertificationRequest
from ..signals_define import certification_request_payment_success


class TestCertificationRequestMetrics(
        ExOCertificationTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_cohorts()

    @patch('utils.metric.metric_mixin.ModelMetricMixin.create_new_metric')
    def test_metric_for_payment_success_is_created(self, mock_create_metric):
        # Prepare data
        certification_request = FakeCertificationRequestFactory(
            cohort=self.cohort_lvl_2,
            certification=self.cohort_lvl_2.certification,
        )

        # Do action
        certification_request_payment_success.send(
            sender=CertificationRequest,
            pk=certification_request.pk,
        )
        # Assertions
        self.assertTrue(mock_create_metric.called)
        action_launched = mock_create_metric.call_args[0][0]
        self.assertEqual(
            action_launched.__class__,
            CustomAction
        )
        # Check METRIC ACTION Name
        self.assertEqual(
            certification_request.get_action(action_launched),
            dict(settings.EXO_CERTIFICATION_METRIC_ACTION_LIST).get(action_launched.verb)
        )
        # Check METRIC ACTION Verb
        self.assertEqual(
            action_launched.verb,
            settings.EXO_CERTIFICATION_METRIC_ACTION_PAY
        )
        # Check METRIC ACTION User
        self.assertEqual(
            certification_request.user.uuid,
            certification_request.get_user(action_launched)
        )
        # Check METRIC VALUE
        self.assertEqual(
            certification_request.get_value(),
            certification_request.price,
        )
        # Check METRIC LABEL
        self.assertEqual(
            certification_request.get_label(action_launched),
            'certification_paid_{}'.format(
                settings.EXO_CERTIFICATION_METRIC_LABELS.get(certification_request.cohort.level)
            )
        )

    @patch('utils.metric.metric_mixin.ModelMetricMixin.create_new_metric')
    def test_metric_for_user_certified(self, mock_create_metric):
        # Prepare data
        consultant = FakeConsultantFactory.create()
        certification_request = FakeCertificationRequestFactory(
            user=consultant.user,
            status=settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_APPROVED,
            certification=self.cohort_lvl_2.certification,
            cohort=self.cohort_lvl_2,
        )
        group = FakeConsultantRoleGroupFactory.create(
            _type=settings.RELATION_CONSULTANT_ROLE_GROUP_TYPE_CONSULTANT)

        certification_role = CertificationRole.objects.get(
            code=settings.EXO_ROLE_CODE_CERTIFICATION_CONSULTANT)

        consultant_role = FakeConsultantRoleFactory.create(
            certification_group=group,
            consultant=consultant,
            certification_role=certification_role)

        # Do action
        user_certified.send(
            sender=consultant_role.__class__,
            user=consultant.user,
            consultant_role=consultant_role,
        )

        # Assertions
        self.assertTrue(mock_create_metric.called)
        action_launched = mock_create_metric.call_args[0][0]
        self.assertEqual(
            action_launched.__class__,
            CustomAction
        )
        # Check METRIC ACTION Name
        self.assertEqual(
            certification_request.get_action(action_launched),
            dict(settings.EXO_CERTIFICATION_METRIC_ACTION_LIST).get(action_launched.verb)
        )
        # Check METRIC ACTION Verb
        self.assertEqual(
            action_launched.verb,
            settings.EXO_CERTIFICATION_METRIC_ACTION_ACQUIRE
        )
        # Check METRIC ACTION User
        self.assertEqual(
            certification_request.user.uuid,
            certification_request.get_user(action_launched)
        )
        # Check METRIC VALUE
        self.assertEqual(
            certification_request.get_value(),
            certification_request.price,
        )
        # Check METRIC LABEL
        self.assertEqual(
            certification_request.get_label(action_launched),
            'certification_granted_{}'.format(
                settings.EXO_CERTIFICATION_METRIC_LABELS.get(certification_request.cohort.level)
            )
        )
