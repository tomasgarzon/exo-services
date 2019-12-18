import json

from rest_framework import serializers

from mail.handlers import mail_handler


class SendMailSerializer(serializers.Serializer):
    template = serializers.CharField(required=True)
    params = serializers.CharField(required=True)
    lang = serializers.CharField(required=False)
    domain = serializers.CharField(required=False)
    file = serializers.FileField(required=False)

    class Meta:
        fields = ['template', 'params', 'lang', 'domain', 'file']

    def create(self, validated_data):
        template = validated_data.get('template')
        params = json.loads(validated_data.get('params'))
        lang = validated_data.get('lang', None)
        domain = validated_data.get('domain', None)
        if validated_data.get('file'):
            params['attachments'] = [validated_data['file']]
        mail_handler.send_mail(
            domain=domain,
            template=template,
            lang=lang,
            **params)
        return validated_data


class ConfigMailSerializer(serializers.Serializer):
    template = serializers.CharField(required=True)
    config = serializers.CharField(required=False)

    class Meta:
        fields = ['template', 'config']

    def create(self, validated_data):
        template = validated_data.get('template')
        config = mail_handler._registry.get(template).config_param
        data = {
            'template': template,
            'config': config
        }
        return data
