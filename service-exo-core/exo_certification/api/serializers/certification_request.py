from rest_framework import serializers

from project.helpers import next_project_url

from ...models import CertificationRequest


class CertificationRequestSerializer(serializers.ModelSerializer):

    level = serializers.CharField(source='certification.level')
    certification_code = serializers.CharField(source='certification.certification_role.code')
    name = serializers.CharField(source='certification.name')
    start_date = serializers.SerializerMethodField(source='cohort.date')
    url = serializers.SerializerMethodField()

    class Meta:
        model = CertificationRequest
        fields = ['status', 'level', 'certification_code', 'name', 'start_date', 'url']

    def get_start_date(self, obj):
        start_date = ''
        if obj.cohort:
            start_date = obj.cohort.date

        return start_date

    def get_url(self, obj):
        url = None

        if hasattr(obj, 'url_foundations'):
            url = obj.url_foundations
        elif obj.cohort and obj.cohort.project:
            url, _ = next_project_url(obj.cohort.project, obj.user)

        return url
