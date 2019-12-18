from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from certification.signals_define import (
    create_certification_credential)
from certification.models import CertificationGroup
from relation.signals_define import add_user_exo_hub


class CertificationProjectWrapper:
    project = None

    def __init__(self, project):
        self.project = project

    def get_data(self, user_from):
        data = {
            'name': '{name} - {location}'.format(
                name=self.project.name,
                location=self.project.location),
            'description': self.project.comment,
            'content_object': self.project,
            '_type': settings.CERTIFICATION_CH_GROUP_WORKSHOP,
            'created_by': user_from,
            'instructor_name': user_from.get_full_name()
        }
        data['issued_on'] = self.project.start
        data['course_name'] = self.project.name
        return data

    def release_simple_credential(self, user_from, user_role):
        ct = ContentType.objects.get_for_model(user_role.project)
        certification_group = CertificationGroup.objects.filter(
            content_type=ct,
            object_id=user_role.project.pk).first()
        if certification_group:
            ct = ContentType.objects.get_for_model(user_role)
            credential, created = certification_group.credentials.get_or_create(
                user=user_role.user,
                content_type=ct,
                object_id=user_role.pk)
            if created:
                create_certification_credential.send(
                    sender=user_role.__class__,
                    certification_group=certification_group,
                    certification_credential=credential,
                    user_from=user_from)

        add_user_exo_hub.send(
            sender=user_role.__class__,
            user=user_role.user,
            exo_hub_code=settings.EXO_HUB_CH_ALUMNI)
        return credential

    def release_group_credential(
            self, user_from, project):
        ct = ContentType.objects.get_for_model(project)
        certification_group = CertificationGroup.objects.filter(
            content_type=ct,
            object_id=project.pk).first()

        users_roles = project.users_roles.filter(certifications__isnull=True)

        if certification_group:
            CertificationGroup.objects.release_group_credential(
                certification_group=certification_group,
                user_from=user_from,
                objects_list=users_roles)

        for user_role in users_roles:
            add_user_exo_hub.send(
                sender=user_role.__class__,
                user=user_role.user,
                exo_hub_code=settings.EXO_HUB_CH_ALUMNI)

        return certification_group
