from rest_framework import serializers

from utils.dates import localize_date

from ...conf import settings
from ...models import Project


class ProjectChangeStatusSerializer(serializers.ModelSerializer):
    new_status = serializers.ChoiceField(
        choices=settings.PROJECT_CH_PROJECT_STATUS,
    )
    date = serializers.DateTimeField(
        format='%m/%d/%Y %H:%M:%S',
        input_formats=['%m/%d/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S'],
    )

    class Meta:
        model = Project
        fields = ['new_status', 'date']

    def is_start(self, value):
        return value == settings.PROJECT_CH_PROJECT_STATUS_STARTED

    def is_finish(self, value):
        return value == settings.PROJECT_CH_PROJECT_STATUS_FINISHED

    def is_waiting(self, value):
        return value == settings.PROJECT_CH_PROJECT_STATUS_WAITING

    def validate(self, data):
        if not data.get('date'):
            raise serializers.ValidationError('No date supplied')
        elif self.is_finish(data.get('new_status')):
            if not self.instance.can_be_finished:
                raise serializers.ValidationError('Project must be started')
            elif self.instance.start >= data.get('date'):
                raise serializers.ValidationError('End date must be after the start date')
        elif self.is_start(data.get('new_status')):
            if not self.instance.can_be_started:
                raise serializers.ValidationError("Project can't be started")
        elif self.is_waiting(data.get('new_status')):
            if not self.instance.can_be_launch:
                raise serializers.ValidationError("Project can't be launch")
        return data

    def validate_date(self, date):
        return localize_date(date, self.instance.timezone)

    def update(self, instance, validated_data):
        if self.is_start(validated_data.get('new_status')):
            instance.set_started(
                user=self.context.get('request').user,
                start_date=validated_data.get('date'),
            )

        elif self.is_finish(validated_data.get('new_status')):
            instance.set_finished(
                user=self.context.get('request').user,
                end_date=validated_data.get('date'),
            )
        elif self.is_waiting(validated_data.get('new_status')):
            instance.launch(
                user=self.context.get('request').user,
                start_date=validated_data.get('date'),
            )
        # Hack to Output serialized data
        instance.new_status = validated_data.get('new_status')
        instance.date = validated_data.get('date')

        return instance
