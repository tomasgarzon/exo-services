from rest_framework import serializers


class SeeSerializer(serializers.Serializer):
    pass


class VoteSerializer(serializers.Serializer):
    pass


class RatingSerializer(serializers.Serializer):
    rating = serializers.IntegerField(required=False)
    comment = serializers.CharField(
        required=False, allow_blank=True,
    )

    def create(self, validated_data):
        answer = validated_data.get('answer')
        user_from = validated_data.get('user_from')
        answer.do_rating(
            user_from,
            rating=validated_data.get('rating'),
            comment=validated_data.get('comment'),
        )
        return validated_data
