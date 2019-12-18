from rest_framework import serializers


class EventAvailableSerializer(serializers.BaseSerializer):

    def to_representation(self, obj):
        return {
            'category': obj[0],
            'type_event_name': obj[1],
        }


class EventTypesSerializer(serializers.BaseSerializer):

    def to_representation(self, obj):
        return {
            'category': obj[0],
            'type_event_name': obj[1],
            'available': obj[2],
        }
