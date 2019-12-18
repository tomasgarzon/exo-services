from rest_framework import serializers


class EmailNotifySerializer(serializers.Serializer):

    email_url = serializers.CharField()
    email_status = serializers.CharField()

    def update(self, instance, validated_data):
        instance.email_url = validated_data.get('email_url')
        instance.email_status = validated_data.get('email_status')
        instance.save(update_fields=['email_url', 'email_status'])

        return instance
