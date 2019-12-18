from rest_framework import serializers

from auth_uuid.utils.user_wrapper import UserWrapper

from utils.drf.user import UserSerializer

from ...models import Applicant
from .answer import AnswerQuestionDetailSerializer
from .feedback import FeedbackApplicantSerializer


class OpportunityApplicantSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()
    userActions = serializers.SerializerMethodField()
    feedbacks = FeedbackApplicantSerializer(many=True)

    class Meta:
        model = Applicant
        fields = '__all__'

    def get_user(self, obj):
        user_wrapper = UserWrapper(user=obj.user)
        return UserSerializer(user_wrapper).data

    def get_answers(self, obj):
        answers = obj.answers.all().order_by('id')
        return AnswerQuestionDetailSerializer(answers, many=True).data

    def get_userActions(self, obj):
        user = self.context.get('request').user
        return obj.user_actions(user)


class OpportunityApplicantSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Applicant
        fields = '__all__'
