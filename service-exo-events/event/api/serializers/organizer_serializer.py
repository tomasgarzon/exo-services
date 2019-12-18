from django.core.exceptions import ValidationError

from rest_framework import serializers

from ...models import Organizer


class OrganizerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organizer
        fields = [
            'uuid',
            'name',
            'email',
            'url',
            'logo',
        ]
        extra_kwargs = {
            'email': {'validators': []},
        }

    def validate(self, attrs):
        uuid = attrs.get('uuid')
        if not uuid:
            try:
                assert attrs.get('name', None)
                assert attrs.get('email', None)
                assert attrs.get('url', None)
            except AssertionError:
                raise ValidationError(
                    'You must define almost Oranizer UUID or Organizer complete \
                    information'
                )

        return attrs
