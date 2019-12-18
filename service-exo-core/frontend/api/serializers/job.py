from rest_framework import serializers


class JobSerializer(serializers.Serializer):
    name = serializers.CharField()
    subtitle = serializers.CharField()
    action = serializers.SerializerMethodField()
    status = serializers.CharField()
    status_desc = serializers.CharField()
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    job_type = serializers.CharField()

    def get_action(self, obj):
        return obj.action
