from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from certification.models import CertificationCredential, CertificationGroup
from exo_role.models import CertificationRole

from consultant.faker_factories import FakeConsultantFactory
from exo_accounts.test_mixins import FakeUserFactory
from relation.models import ConsultantRole
from utils.faker_factory import faker

CONSULTANT = settings.EXO_ROLE_CODE_CERTIFICATION_CONSULTANT
COACH = settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH


class EcosystemAPITestMixin:

    def crete_certification_groups(self):
        self.consultant_group = CertificationGroup.objects.create(
            name=faker.name(),
            _type=settings.CERTIFICATION_CH_GROUP_CH_TYPE_CONSULTANT,
        )
        self.coach_group = CertificationGroup.objects.create(
            name=faker.name(),
            _type=settings.CERTIFICATION_CH_GROUP_CH_TYPE_COACH,
        )

    def create_user_credentials(self, user, group, consultant_role):
        return CertificationCredential.objects.create(
            user=user,
            group=group,
            object_id=consultant_role.pk,
            content_type=ContentType.objects.get_for_model(consultant_role)
        )

    def add_certifications_to_consultant(self, consultant, certified_roles):
        for role in certified_roles:
            if role == CONSULTANT:
                group = self.consultant_group
            elif role == COACH:
                group = self.coach_group
            else:
                return False
            consultant_role = ConsultantRole.objects.create(
                certification_role=CertificationRole.objects.get(code=role),
                consultant=consultant,
            )
            self.create_user_credentials(
                consultant.user,
                group,
                consultant_role,
            )

    def initialize_consultants(self):
        self.crete_certification_groups()
        consultants = [
            (4, 'Sevilla,CONSULTANT Spain', [CONSULTANT, COACH]),
            (2, 'London, United Kingdom', [CONSULTANT]),
            (6, 'Barcelona, Spain', [CONSULTANT]),
            (18, 'Rostock, Germany', [CONSULTANT, COACH]),
            (7, 'Berlin, Germany', [CONSULTANT, COACH]),
            (14, 'Tokyo, Japan', [CONSULTANT]),
            (8, 'Buenos Aires, Argentina', []),
            (3, 'Munich, Germany', [CONSULTANT])
        ]

        for num_project, location, certified_roles in consultants:
            user = FakeUserFactory.create(
                password='123456',
                is_active=True,
                location=location)
            consultant = FakeConsultantFactory(
                user=user,
                status=settings.CONSULTANT_STATUS_CH_ACTIVE)
            self.add_certifications_to_consultant(consultant, certified_roles)

            member = consultant.user.ecosystem_member
            member.num_projects = num_project
            member.save()
            self.user = user

        FakeConsultantFactory.create_batch(
            size=4,
            user__location='Jaen, Spain',
            status=settings.CONSULTANT_STATUS_CH_DISABLED)

        FakeConsultantFactory.create_batch(
            size=16,
            user__location='Granada, Spain',
            status=settings.CONSULTANT_STATUS_CH_ACTIVE)
