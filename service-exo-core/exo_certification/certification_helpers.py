from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from certification.signals_define import create_certification_group_credential
from certification.tasks import CreateAccredibleSimpleCredentialTask

from relation.signals_define import add_user_exo_hub, user_certified


class CertificationConsultantRoleWrapper:

    def _sync_users(self, consultant_role_group, consultant_roles):
        for consultant_role in consultant_roles:
            exo_hub_code = dict(
                settings.CERTIFICATION_CH_HUB_NAME,
            ).get(consultant_role_group._type, '')
            if exo_hub_code:
                add_user_exo_hub.send(
                    sender=consultant_role.consultant.user.__class__,
                    user=consultant_role.consultant.user,
                    exo_hub_code=exo_hub_code)
            user_certified.send(
                sender=consultant_role.consultant.user.__class__,
                user=consultant_role.consultant.user,
                consultant_role=consultant_role)

    def create_group_and_credentials(self, user_from, consultant_role_group, course_name):
        data = {
            'name': consultant_role_group.name,
            'description': consultant_role_group.description,
            'content_object': consultant_role_group,
            '_type': consultant_role_group._type,
            'created_by': user_from,
            'instructor_name': user_from.get_full_name(),
        }
        data['issued_on'] = consultant_role_group.issued_on
        data['course_name'] = course_name
        create_certification_group_credential.send(
            sender=consultant_role_group.__class__,
            user_from=user_from,
            related_objects_list=consultant_role_group.consultant_roles.all(),
            **data)

        self._sync_users(
            consultant_role_group=consultant_role_group,
            consultant_roles=consultant_role_group.consultant_roles.all(),
        )

    def update_group_with_more_credentials(self, user_from, consultant_role_group, consultant_roles):
        certification_group = consultant_role_group.certification_groups.all().first()

        for related_object in consultant_roles:
            credential = certification_group.credentials.create(
                user=related_object.user,
                content_type=ContentType.objects.get_for_model(related_object),
                object_id=related_object.pk)
            CreateAccredibleSimpleCredentialTask().s(
                credential_id=credential.pk).apply_async()

        self._sync_users(
            consultant_role_group,
            consultant_roles,
        )
