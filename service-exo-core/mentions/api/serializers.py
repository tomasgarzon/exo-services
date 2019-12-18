from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from exo_mentions.api.serializers import SearchMentionResultsSerializer

from circles.models import Circle


class SearchMentionSerializer(serializers.Serializer):

    search = serializers.CharField(required=False, allow_blank=True)
    circle_pk = serializers.CharField()

    def validate_circle_pk(self, value):
        try:
            actor = self.context.get('request').user

            circle = Circle.objects.get(pk=value)
            assert circle.check_user_can_post(actor, False)

        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                'Circle with id {} object does not exist.'.format(
                    value,
                )
            )

        except AssertionError:
            raise serializers.ValidationError(
                'You are not able to mention at this circle')

        return value


class UserMentionResultsSerializer(SearchMentionResultsSerializer):
    url = serializers.URLField()
