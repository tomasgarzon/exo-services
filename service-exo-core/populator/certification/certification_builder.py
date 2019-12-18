from django.conf import settings

from certification.models import CertificationGroup
from exo_role.models import CertificationRole
from relation.models import ConsultantRoleCertificationGroup, ConsultantRole
from relation.signals_define import add_user_exo_hub, user_certified

from populate.populator.builder import Builder


class CertificationBuilder(Builder):

    def create_object(self):
        _type = self.data.get('type')
        certifications = self.data.get('certifications')
        certification_role = CertificationRole.objects.get(code=self.data.get('certification_role'))
        consultants = [cer.get('consultant') for cer in certifications]

        group = self.create_consultant_role_certification_group(
            name=self.data.get('name'),
            description=self.data.get('description'),
            _type=_type,
            created_by=self.data.get('created_by'),
            issued_on=self.data.get('issued_on'))

        self.update_roles(
            consultant_role_group=group,
            consultants=consultants,
            certification_role=certification_role)

        self.create_certification_group(
            consultant_role_group=group,
            certifications=certifications,
            course_name=self.data.get('course_name'),
            instructor_name=self.data.get('instructor_name'),
        )

        return group

    def create_consultant_role_certification_group(self, name, description, _type, created_by, issued_on):
        return ConsultantRoleCertificationGroup.objects.create(
            name=name,
            description=description,
            _type=_type,
            created_by=created_by,
            issued_on=issued_on)

    def update_roles(self, consultant_role_group, consultants, certification_role):

        for consultant in consultants:
            ConsultantRole.objects.create(
                consultant=consultant,
                certification_role=certification_role,
                certification_group=consultant_role_group)

    def create_certification_group(self, consultant_role_group, certifications, course_name, instructor_name):
        data = {
            'name': consultant_role_group.name,
            'description': consultant_role_group.description,
            'content_object': consultant_role_group,
            '_type': consultant_role_group._type,
            'created_by': consultant_role_group.created_by,
            'instructor_name': instructor_name,
        }
        data['issued_on'] = consultant_role_group.issued_on
        data['course_name'] = course_name
        certification_group = CertificationGroup.objects.create_group_and_credentials(
            user_from=consultant_role_group.created_by,
            related_objects_list=consultant_role_group.consultant_roles.all(),
            **data)

        for certification in certifications:
            certification_group.credentials.filter(
                user=certification.get('consultant').user).update(
                    accredible_id=certification.get('accredible_id'),
                    accredible_url=certification.get('accredible_url'),
                    status=settings.CERTIFICATION_CH_STATUS_GENERATED)

        for consultant_role in consultant_role_group.consultant_roles.all():
            exo_hub_code = dict(settings.CERTIFICATION_CH_HUB_NAME).get(
                consultant_role_group._type, '')

            if exo_hub_code:
                add_user_exo_hub.send(
                    sender=consultant_role.consultant.user.__class__,
                    user=consultant_role.consultant.user,
                    exo_hub_code=exo_hub_code)

            user_certified.send(
                sender=consultant_role.consultant.user.__class__,
                user=consultant_role.consultant.user,
                consultant_role=consultant_role)
