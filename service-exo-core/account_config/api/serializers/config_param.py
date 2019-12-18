from rest_framework import serializers

from ...models import ConfigParam


class ConfigParamSerializer(serializers.ModelSerializer):

    value = serializers.SerializerMethodField()

    class Meta:
        model = ConfigParam
        fields = ['name', 'param_type', 'group', 'id', 'value']

    def get_value(self, obj):
        agent = self.context.get('agent')
        try:
            value = obj.get_value_for_agent(agent)
        except ValueError:
            value = None
        return value


class ConfigParamUserSerializer(serializers.Serializer):

    value = serializers.CharField()

    def validate_value(self, value):
        try:
            return eval(value)
        except ValueError:
            raise serializers.ValidationError('Value has an incorrect value')

    def create(self, validated_data):
        agent = self.context.get('agent')
        value = validated_data.get('value')
        config_param = validated_data.get('config_param')
        config_param.set_value_for_agent(agent, value)
        return validated_data
