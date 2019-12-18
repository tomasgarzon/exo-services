from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from auth_uuid.utils.user_wrapper import UserWrapper

from certification.signals_define import create_certification_credential
from certification.models import CertificationGroup


class CertificationWorkshopWrapper:
    event = None

    def __init__(self, event):
        self.event = event

    def get_data(self, user_from):
        event_owner = UserWrapper(user=self.event.created_by)
        data = {
            'name': '{name} - {location}'.format(
                name=self.event.title,
                location=self.event.location_for_certification),
            'description': self.event.description_for_certification,
            'content_object': self.event,
            'instructor_name': event_owner.get_full_name(),
            '_type': settings.CERTIFICATION_CH_GROUP_WORKSHOP,
            'created_by': user_from,
        }
        data['issued_on'] = self.event.start
        data['course_name'] = self.event.title
        return data

    def release_simple_credential(self, user_from, participant):
        credential = None
        event = participant.event
        ct = ContentType.objects.get_for_model(event)
        certification_group = CertificationGroup.objects.filter(
            content_type=ct,
            object_id=event.pk,
        ).first()
        if certification_group:
            ct = ContentType.objects.get_for_model(participant)
            credential, created = certification_group.credentials.get_or_create(
                user=participant.user,
                content_type=ct,
                object_id=participant.pk,
            )
            if created:
                create_certification_credential.send(
                    sender=participant.__class__,
                    certification_group=certification_group,
                    certification_credential=credential,
                    user_from=user_from)
        return credential

    def release_group_credential(self, user_from, event):
        ct = ContentType.objects.get_for_model(event)
        certification_group = CertificationGroup.objects.filter(
            content_type=ct,
            object_id=event.pk).first()

        participants = event.participants.filter(
            certifications__isnull=True,
        ).filter_by_role_name(settings.EVENT_SPEAKER_NAME)

        if certification_group:
            CertificationGroup.objects.release_group_credential(
                certification_group=certification_group,
                user_from=user_from,
                objects_list=participants)

        return certification_group
