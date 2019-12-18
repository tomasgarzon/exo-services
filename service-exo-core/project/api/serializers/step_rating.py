from django.conf import settings

from rest_framework import serializers


class Rating:
    rate = None
    feedback = None
    comments = ''
    target = None

    def build_from_team_step(self, team_step, user):
        self.rate = team_step.get_rating_for_user(user)
        self.feedback = team_step.get_feedback_for_user(user)
        relation_type, _ = team_step.target_rating(user)
        self.target = relation_type.value

        if team_step.get_feedback_for_user(user):
            last_feedback = team_step.get_last_action_feedback(
                user=user,
                verb=settings.TEAM_ACTION_COMMENT_WEEKLY,
            )
            self.comments = last_feedback.description


class RatingSerializer(serializers.Serializer):
    rate = serializers.IntegerField(required=False)
    feedback = serializers.IntegerField(required=False)
    comments = serializers.CharField(required=False)
    target = serializers.IntegerField(required=False)


class StepRatingSerializer(serializers.Serializer):
    rate = serializers.IntegerField(required=True)
    feedback = serializers.IntegerField(required=True)
    comments = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True)

    def create(self, validated_data):
        team = self.context.get('view').team
        step = self.context.get('view').get_object()
        team_step = team.steps.get(step=step)
        user_from = validated_data.get('user_from')

        team_step.do_rating(
            user_from=user_from,
            rating=validated_data.get('rate'),
        )
        team_step.do_feedback(
            user_from=user_from,
            rating=validated_data.get('feedback'),
            comment=validated_data.get('comments'))

        rating = Rating()
        rating.rate = validated_data.get('rate')
        rating.feedback = validated_data.get('feedback')
        rating.comments = validated_data.get('comments')
        relation_type, _ = team_step.target_rating(user_from)
        rating.target = relation_type.value
        return rating
