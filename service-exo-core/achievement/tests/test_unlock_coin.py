from django.conf import settings

from core.models import Language
from industry.models import Industry
from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from utils.faker_factory import faker
from relation.models import ConsultantExOAttribute

from ..models import Achievement, UserReward


class UnlockCoinTests(SuperUserTestMixin, DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()

    def test_create_achievement_reward(self):
        consultant = FakeConsultantFactory.create()

        Achievement.objects.create_reward_for_consultant(
            consultant=consultant,
            number_of_coins=10,
        )
        user_reward = UserReward.objects.filter(user=consultant.user).first()
        self.assertIsNotNone(user_reward)
        self.assertEqual(
            int(user_reward.extra_data['coins']),
            10,
        )

    def test_not_create_achievement_reward(self):
        consultant = FakeConsultantFactory.create()

        Achievement.objects.create_reward_for_consultant(
            consultant=consultant,
        )
        user_reward = UserReward.objects.filter(user=consultant.user).first()
        self.assertIsNone(user_reward)

    def test_unlock_achievement_reward(self):
        consultant = FakeConsultantFactory.create()

        user_achievement = Achievement.objects.create_reward_for_consultant(
            consultant=consultant,
            number_of_coins=10,
        )
        user_reward = UserReward.objects.filter(user=consultant.user).first()
        user = consultant.user
        user.profile_picture_origin = settings.EXO_ACCOUNTS_PROFILE_PICTURE_CH_USER
        user.location = faker.city() + ', ' + faker.country()
        user.about_me = faker.paragraph()
        user.save()
        user_achievement.refresh_from_db()
        user_reward.refresh_from_db()
        self.assertTrue(user_achievement.is_pending)
        self.assertTrue(user_reward.is_pending)
        for language in Language.objects.all():
            consultant.languages.add(language)
        for consultant_exo_attribute in ConsultantExOAttribute.objects.filter(consultant=consultant):
            consultant_exo_attribute.level = 3
            consultant_exo_attribute.save()

        for industry in Industry.objects.all()[:5]:
            consultant.industries.create(
                industry=industry,
                level=3,
            )
        user_achievement.refresh_from_db()
        user_reward.refresh_from_db()
        self.assertTrue(user_achievement.is_completed)
        self.assertTrue(user_reward.is_completed)
