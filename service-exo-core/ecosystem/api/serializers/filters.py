from rest_framework import serializers

from core.models import Language
from exo_role.models import ExORole, CertificationRole
from exo_activity.models import ExOActivity
from exo_attributes.models import ExOAttribute
from exo_hub.models import ExOHub
from industry.models import Industry
from keywords.models import Keyword


class EcosystemFilterSerializer(serializers.Serializer):
    title = serializers.CharField()
    queryparam = serializers.CharField()
    multiselect = serializers.BooleanField()
    items = serializers.ListField()


class ExOHubFilterSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='_type')
    default = serializers.BooleanField()

    class Meta:
        model = ExOHub
        fields = ['name', 'value', 'default']


class ExORoleFilterSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='code')
    default = serializers.BooleanField()

    class Meta:
        model = ExORole
        fields = ['name', 'value', 'default']


class CertificationRoleFilterSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='code')
    default = serializers.BooleanField()

    class Meta:
        model = CertificationRole
        fields = ['name', 'value', 'default']


class ExOAttributeFilterSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='name')
    default = serializers.BooleanField()

    class Meta:
        model = ExOAttribute
        fields = ['name', 'value', 'default']


class IndustryFilterSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='name')
    default = serializers.BooleanField()

    class Meta:
        model = Industry
        fields = ['name', 'value', 'default']


class LanguageFilterSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='name')
    default = serializers.BooleanField()

    class Meta:
        model = Language
        fields = ['name', 'value', 'default']


class KeywordFilterSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='name')
    default = serializers.BooleanField()

    class Meta:
        model = Keyword
        fields = ['name', 'value', 'default']


class ExOActivityFilterSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='code')
    default = serializers.BooleanField()

    class Meta:
        model = ExOActivity
        fields = ['name', 'value', 'default']
