from django.test import TestCase
from django.conf import settings

from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from consultant.faker_factories import FakeConsultantFactory
from exo_activity.models import ExOActivity

from ..models import ConfigParam


class ConfigParamTestCase(TestCase):

    def setUp(self):
        self.user = FakeUserFactory.create()
        self.consultant = FakeConsultantFactory.create()

    def test_config_user(self):
        # PREPARE DATA
        config_param = ConfigParam.objects.get(name='new_answer')

        # ASSERTS
        self.assertFalse(config_param.get_value_for_agent(self.user))

        # DO ACTION
        config_param.set_value_for_agent(self.user, True)

        # ASSERTS
        self.assertTrue(config_param.get_value_for_agent(self.user))

    def test_config_consultant(self):
        # PREPARE DATA
        config_param = ConfigParam.objects.get(name='new_post')

        # ASSERTS
        self.assertTrue(config_param.get_value_for_agent(self.consultant))

        # DO ACTION
        config_param.set_value_for_agent(self.consultant, False)
        self.assertFalse(config_param.get_value_for_agent(self.consultant))

    def test_config_consultant_no_advising(self):
        # PREPARE DATA
        config_param = ConfigParam.objects.get(name='new_question_from_project')

        # ASSERTS
        with self.assertRaises(ValueError):
            config_param.get_value_for_agent(self.consultant)

    def test_config_consultant_advising(self):
        # PREPARE DATA
        config_param = ConfigParam.objects.get(name='new_question_from_project')
        exo_consulting = ExOActivity.objects.get(
            code=settings.EXO_ACTIVITY_CH_ACTIVITY_CONSULTING)
        exo_activity, _ = self.consultant.exo_profile.exo_activities.get_or_create(
            exo_activity=exo_consulting)
        exo_activity.enable()

        # ASSERTS
        self.assertTrue(config_param.get_value_for_agent(self.consultant))
        # DO ACTION
        config_param.set_value_for_agent(self.consultant, False)
        self.assertFalse(config_param.get_value_for_agent(self.consultant))
