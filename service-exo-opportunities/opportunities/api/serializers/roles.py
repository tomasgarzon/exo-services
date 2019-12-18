from rest_framework import serializers

from django.conf import settings

from exo_role.models import ExORole, Category

from ...certification_helper import CERTIFICATION_REQUIREMENTS


class CategoryExORoleSerializer(serializers.ModelSerializer):
    certifications = serializers.SerializerMethodField()
    is_other = serializers.SerializerMethodField()

    class Meta:
        model = ExORole
        fields = [
            'name',
            'code',
            'description',
            'certifications',
            'is_other',
        ]

    def get_certifications(self, obj):
        code = obj.code
        return CERTIFICATION_REQUIREMENTS.get(code, [])

    def get_is_other(self, obj):
        return obj.code in [
            settings.EXO_ROLE_CODE_OTHER_OTHER,
            settings.EXO_ROLE_CODE_SPRINT_OTHER,
        ]


class CategorySerializer(serializers.ModelSerializer):
    roles = CategoryExORoleSerializer(many=True)

    class Meta:
        model = Category
        fields = [
            'name',
            'code',
            'description',
            'roles',
        ]
