from rest_framework import serializers

from ...models import Survey


class SurveySerializer(serializers.ModelSerializer):

    class Meta:
        model = Survey
        fields = [
            'name', 'slug', 'pk',
            'created',
            'send_results', 'show_results',
            'language',
        ]

    def create(self, validated_data):
        user_from = validated_data.pop('user_from')
        return Survey.objects.create(
            created_by=user_from,
            **validated_data)


class SurveyDetailSerializer(serializers.ModelSerializer):
    total_answers = serializers.IntegerField(source='surveys_filled.count')

    class Meta:
        model = Survey
        fields = [
            'name', 'slug', 'pk',
            'send_results', 'show_results',
            'total_answers', 'created', 'public_url',
            'language',
        ]
