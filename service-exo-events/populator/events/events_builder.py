from django.conf import settings
from django.contrib.auth import get_user_model

from exo_role.models import Category, ExORole
from populate.populator.builder import Builder

from event.models import Event, Participant

User = get_user_model()


class EventsBuilder(Builder):

    def create_object(self):
        return self.create_event(
            uuid=self.data.get('uuid', None),
            _status=self.data.get('status', settings.EVENT_CH_STATUS_DEFAULT),
            user_from=self.data.get('created_by'),
            user_from_name=self.data.get('created_by_full_name'),
            title=self.data.get('title'),
            sub_title=self.data.get('sub_title'),
            description=self.data.get('description'),
            start=self.data.get('start'),
            end=self.data.get('end'),
            category=self.data.get('category'),
            type_event_other=self.data.get('type_event_other'),
            follow_type=self.data.get('follow_type'),
            location=self.data.get('location'),
            url=self.data.get('url'),
            languages=self.data.get('languages'),
            show_price=self.data.get('show_price'),
            amount=self.data.get('amount'),
            currency=self.data.get('currency'),
            organizers=self.data.get('organizers', []),
            participants=self.data.get('participants', []),
        )

    def create_event(self, uuid, *args, **kwargs):
        participants = kwargs.pop('participants', [])
        created_by_user_name = kwargs.pop('user_from_name')
        if uuid is not None:
            kwargs['uuid'] = uuid
        event = Event.objects.create_event(
            category=Category.objects.get(code=kwargs.pop('category')),
            force_retrieve_user_data=False,
            **kwargs,
        )
        event.created_by_full_name = created_by_user_name
        event.save()

        for participant_data in participants:
            participant, created = Participant.objects.get_or_create(
                user=participant_data.get('user'),
                event=event,
            )
            participant.user_name = participant_data.get('user_name')
            participant.user_email = participant_data.get('user_email')
            participant.order = participant_data.get('order')
            participant.exo_role = ExORole.objects.get(code=participant_data.get('role'))
            participant.status = participant_data.get('status')
            participant.save()

            event.participants.add(participant)
        return event
