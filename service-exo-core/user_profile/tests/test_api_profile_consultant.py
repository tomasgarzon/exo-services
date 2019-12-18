import random

from django.urls import reverse
from django.conf import settings

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from core.models import Language
from utils.faker_factory import faker
from relation.models import (
    ConsultantExOAttribute,
    ConsultantIndustry, ConsultantKeyword
)
from industry.models import Industry
from exo_activity.models import ExOActivity
from keywords.models import Keyword


def get_fake_name():
    return faker.word() + faker.numerify()


class ProfileConsultantAPITests(
        SuperUserTestMixin,
        DjangoRestFrameworkTestCase
):

    def test_change_languages_consultant(self):
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:change-profile-languages',
            kwargs={'pk': consultant.pk},
        )
        data = {
            'languages': [lang.pk for lang in Language.objects.all()[:2]],
        }
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        consultant.refresh_from_db()
        self.assertEqual(consultant.languages.count(), 2)

    def test_change_languages_optional(self):
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:change-profile-languages',
            kwargs={'pk': consultant.pk},
        )
        consultant.languages.add(Language.objects.all()[0])
        data = {
            'languages': [],
        }
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        consultant.refresh_from_db()
        self.assertEqual(consultant.languages.count(), 0)

    def test_change_mtp_consultant(self):
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:change-profile-mtp',
            kwargs={'pk': consultant.pk},
        )
        data = {
            'personal_mtp': faker.paragraph(),
            'mtp_mastery': 1,
        }
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        consultant.refresh_from_db()
        consultant.exo_profile.refresh_from_db()
        self.assertEqual(
            consultant.exo_profile.personal_mtp,
            data['personal_mtp'],
        )
        self.assertEqual(
            consultant.exo_profile.mtp_mastery,
            data['mtp_mastery'],
        )

    def test_change_purpose(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:change-profile-mtp',
            kwargs={'pk': consultant.pk},
        )
        exo_profile = consultant.exo_profile
        exo_profile.mtp_mastery = 3
        exo_profile.save()

        data = {
            'personal_mtp': faker.paragraph(),
        }
        # DO ACTION
        response = self.client.put(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        consultant.refresh_from_db()
        consultant.exo_profile.refresh_from_db()
        self.assertEqual(
            consultant.exo_profile.personal_mtp,
            data['personal_mtp'],
        )
        self.assertEqual(
            consultant.exo_profile.mtp_mastery,
            3,
        )

    def test_change_areas_consultant(self):
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:change-profile-core-pillars',
            kwargs={'pk': consultant.pk},
        )
        data = {
            'areas': [settings.EXO_AREA_CH_AREA_ORGANIZATION],
        }
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(consultant.exo_areas.count(), 1)
        data = {
            'areas': [
                settings.EXO_AREA_CH_AREA_PEOPLE,
                settings.EXO_AREA_CH_AREA_INSTITUTION,
            ],
        }
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(consultant.exo_areas.count(), 2)

    def test_change_availability_consultant(self):
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:change-profile-availability',
            kwargs={'pk': consultant.pk},
        )
        data = {
            'availability': 'W',
            'availability_hours': 25,
        }
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        consultant.refresh_from_db()
        consultant.exo_profile.refresh_from_db()
        self.assertEqual(consultant.exo_profile.availability, 'W')
        self.assertEqual(consultant.exo_profile.availability_hours, 25)

    def test_change_exo_attributes_consultant(self):
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:change-profile-exo-attributes',
            kwargs={'pk': consultant.pk},
        )

        data = {'exo_attributes': []}
        for attr in consultant.exo_attributes.all():
            value = {'level': random.randint(0, 5), 'id': attr.pk}
            data['exo_attributes'].append(value)
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        consultant.refresh_from_db()

        for value in data.get('exo_attributes'):
            attr = ConsultantExOAttribute.objects.get(pk=value['id'])
            self.assertEqual(attr.level, value.get('level'))
            self.assertEqual(attr.consultant, consultant)

    def test_change_industries_consultant(self):
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:change-profile-industries',
            kwargs={'pk': consultant.pk},
        )

        data = {'industries': []}
        value = {
            'name': Industry.objects.first(
            ).name, 'level': random.randint(1, 3),
        }
        data['industries'].append(value)
        for k in range(random.randint(1, 5)):
            value = {'level': random.randint(1, 3), 'name': get_fake_name()}
            data['industries'].append(value)
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        consultant.refresh_from_db()
        # new industries created by the user
        for industry_name in data.get('industries')[1:]:
            self.assertTrue(
                Industry.objects.filter(
                    name=industry_name['name'],
                    public=False,
                    created_by=consultant.user,
                ).exists(),
            )
        # Industries for the user
        for value in data.get('industries'):
            attr = ConsultantIndustry.objects.filter(
                consultant=consultant,
                industry__name=value.get('name'),
                level=value.get('level'),
            ).first()
            self.assertIsNotNone(attr)

    def test_change_activities_consultant(self):
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        self.assertEqual(consultant.exo_profile.exo_activities.count(), 0)
        url = reverse(
            'api:profile:change-profile-activities',
            kwargs={'pk': consultant.pk},
        )
        data = {
            'exo_activities': [
                ExOActivity.objects.all()[1].code,
                ExOActivity.objects.all()[2].code,
            ],
        }
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        consultant.refresh_from_db()
        consultant.exo_profile.refresh_from_db()
        self.assertEqual(consultant.exo_profile.exo_activities.count(), 2)

    def test_change_keywords_consultant(self):
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:change-profile-keywords',
            kwargs={'pk': consultant.pk},
        )

        data = {'expertise': []}
        key = Keyword.objects.create(
            name=get_fake_name(), public=True,
        )
        key.tags.add(settings.KEYWORDS_CH_EXPERTISE)
        value = {'name': key.name, 'level': random.randint(1, 3)}
        data['expertise'].append(value)
        for k in range(random.randint(1, 5)):
            value = {'level': random.randint(1, 3), 'name': get_fake_name()}
            data['expertise'].append(value)
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        consultant.refresh_from_db()
        total_keywords = len(data.get('expertise'))
        # new keywords created by the user
        for keyword_name in data.get('expertise')[1:]:
            self.assertTrue(
                Keyword.objects.filter(
                    name=keyword_name['name'],
                    public=False,
                    created_by=consultant.user,
                ).exists(),
            )
        # keywords for the user
        for value in data.get('expertise'):
            attr = ConsultantKeyword.objects.filter(
                consultant=consultant,
                keyword__name=value.get('name'),
                level=value.get('level'),
            ).first()
            self.assertIsNotNone(attr)
        for key in ConsultantKeyword.objects.filter(consultant=consultant):
            keyword = key.keyword
            self.assertTrue(
                settings.KEYWORDS_CH_TECHNOLOGY in keyword.tags
                or settings.KEYWORDS_CH_EXPERTISE in keyword.tags,
            )

        data = {'technology': []}
        key = Keyword.objects.create(
            name=get_fake_name(), public=True,
        )
        key.tags.add(settings.KEYWORDS_CH_TECHNOLOGY)
        value = {'name': key.name, 'level': random.randint(1, 3)}
        data['technology'].append(value)
        for k in range(random.randint(1, 5)):
            value = {'level': random.randint(1, 3), 'name': get_fake_name()}
            data['technology'].append(value)
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        consultant.refresh_from_db()
        total_keywords += len(data.get('technology'))
        # new keywords created by the user
        for keyword_name in data.get('technology')[1:]:
            self.assertTrue(
                Keyword.objects.filter(
                    name=keyword_name['name'],
                    public=False,
                    created_by=consultant.user,
                ).exists(),
            )
        # keywords for the user
        for value in data.get('technology'):
            attr = ConsultantKeyword.objects.filter(
                consultant=consultant,
                keyword__name=value.get('name'),
                level=value.get('level'),
            ).first()
            self.assertIsNotNone(attr)
        self.assertEqual(
            ConsultantKeyword.objects.filter(consultant=consultant).count(),
            total_keywords,
        )
        for key in ConsultantKeyword.objects.filter(consultant=consultant):
            keyword = key.keyword
            self.assertTrue(
                settings.KEYWORDS_CH_TECHNOLOGY in keyword.tags
                or settings.KEYWORDS_CH_EXPERTISE in keyword.tags,
            )

    def test_keywords_redis_consultant(self):
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:change-profile-keywords',
            kwargs={'pk': consultant.pk},
        )

        data = {'expertise': []}
        for k in range(3):
            value = {'level': random.randint(1, 3), 'name': get_fake_name()}
            data['expertise'].append(value)
        self.client.put(url, data=data, format='json')

        data = {'technology': []}
        for k in range(3):
            value = {'level': random.randint(1, 3), 'name': get_fake_name()}
            data['technology'].append(value)
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        url = reverse(
            'api:profile:change-profile-industries',
            kwargs={'pk': consultant.pk},
        )

        data = {'industries': []}
        for k in range(4):
            value = {'level': random.randint(1, 3), 'name': get_fake_name()}
            data['industries'].append(value)
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        url = reverse(
            'api:profile:change-profile-exo-attributes',
            kwargs={'pk': consultant.pk},
        )

        data = {'exo_attributes': []}
        for attr in consultant.exo_attributes.all():
            value = {'level': random.randint(0, 5), 'id': attr.pk}
            data['exo_attributes'].append(value)
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
