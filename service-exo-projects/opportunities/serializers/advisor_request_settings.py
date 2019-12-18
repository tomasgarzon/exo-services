from rest_framework import serializers

from ..models import AdvisorRequestSettings


class AdvisorRequestSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdvisorRequestSettings
        exclude = ('project', 'exo_role', 'certification_required')
