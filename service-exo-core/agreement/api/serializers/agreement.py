from rest_framework import serializers

from ...models import Agreement, UserAgreement


class AgreementSerializer(serializers.ModelSerializer):
    pdf = serializers.CharField(source='file_url')

    class Meta:
        model = Agreement
        fields = [
            'description',
            'html',
            'name',
            'pdf',
            'pk',
            'status',
            'version',
        ]


class UserAgreementSerializer(serializers.ModelSerializer):
    agreement = AgreementSerializer()

    class Meta:
        model = UserAgreement
        fields = [
            'agreement',
            'status',
        ]
