from rest_framework import serializers

from industry.models import Industry

from ...models import SurveyFilled, Answer, Result


class AnswerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='question.name')
    section = serializers.CharField(source='question.section')

    class Meta:
        model = Answer
        fields = ['order', 'name', 'value', 'section']


class ResultSerializer(serializers.ModelSerializer):
    section_name = serializers.CharField(source='get_section_display')

    class Meta:
        model = Result
        fields = ['section', 'section_name', 'score', 'max_score']


class SurveyFilledSerializer(serializers.ModelSerializer):
    results = ResultSerializer(many=True)
    answers = AnswerSerializer(many=True)
    industry = serializers.PrimaryKeyRelatedField(
        queryset=Industry.objects.all(),
        required=False,
        allow_null=True)
    industry_name = serializers.SerializerMethodField()

    class Meta:
        model = SurveyFilled
        fields = [
            'name', 'organization', 'email',
            'total',
            'answers',
            'results',
            'industry',
            'pk',
            'industry_name'
        ]

    def get_industry_name(self, obj):
        return obj.industry.name if obj.industry else ''
