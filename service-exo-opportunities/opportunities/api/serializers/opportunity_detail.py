from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from rest_framework import serializers

from auth_uuid.utils.user_wrapper import UserWrapper
from exo_role.api.serializers import ExORoleSerializer, CertificationRoleSerializer
from files.api.serializers.uploaded_file_reverse import UploadedFileRelatedGenericSerializer

from keywords.serializers import KeywordSerializer
from languages.serializers import LanguageSerializer
from utils.drf.user import UserSerializer

from ...models import Opportunity, OpportunityStatus
from .applicant import OpportunityApplicantSerializer
from .mixin import OpportunityUserMixin
from .question import QuestionSerializer
from .opportunity_budget import BudgetSerializer


class OpportunityStatusSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityStatus
        fields = '__all__'

    def get_user(self, obj):
        user_wrapper = UserWrapper(user=obj.user)
        return UserSerializer(user_wrapper).data


class OpportunityDetailSerializer(OpportunityUserMixin, serializers.ModelSerializer):
    keywords = KeywordSerializer(many=True, required=False)
    languages = LanguageSerializer(many=True, required=False)
    userStatus = serializers.SerializerMethodField()
    userActions = serializers.SerializerMethodField()
    applicants = serializers.SerializerMethodField()
    myApplicant = serializers.SerializerMethodField()
    requestedBy = serializers.SerializerMethodField()
    newApplicants = serializers.SerializerMethodField()
    questions = serializers.SerializerMethodField()
    budgets = BudgetSerializer(many=True)
    status = serializers.CharField()
    users_tagged = serializers.SerializerMethodField()
    exo_role = ExORoleSerializer()
    certification_required = CertificationRoleSerializer()
    files = serializers.SerializerMethodField()
    info_detail = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
            'pk', 'slug', 'uuid',
            'title', 'description', 'keywords', 'questions',
            'languages',
            'mode', 'location', 'place_id', 'location_url',
            'start_date', 'modified', 'created',
            'duration_unity', 'duration_value',
            'exo_role', 'certification_required', 'entity',
            'other_role_name', 'other_category_name',
            'userStatus', 'userActions',
            'budgets',
            'applicants', 'myApplicant', 'requestedBy',
            'newApplicants', 'files',
            'num_positions', 'deadline_date',
            'status', 'users_tagged', 'target',
            'has_been_edited', 'info_detail',
        ]
        read_only_fields = ['slug', 'modified', 'uuid']

    @property
    def is_admin_action(self):
        action = ''
        try:
            action_by_default = self.context.get('view').action
            action = self.context.get('action', action_by_default)
        except Exception:
            pass
        return action in [
            'admin', 'assign', 'close', 'reject', 're_open']

    def get_applicants(self, obj):
        if self.is_admin_action:
            queryset = obj.applicants_info.all().order_by_status()
            return OpportunityApplicantSerializer(
                queryset, many=True,
                context=self.context).data
        return []

    def get_myApplicant(self, obj):
        context = self.context.get('request')
        my_applicant = obj.get_applicants_for_user(context.user).first()
        if not my_applicant:
            return None
        return OpportunityApplicantSerializer(
            instance=my_applicant,
            context=self.context).data

    def get_userActions(self, obj):
        return obj.user_actions(
            self.context.get('request').user,
            remove_admin_actions=not self.is_admin_action,
        )

    def get_newApplicants(self, obj):
        user = self.context.get('request').user
        ct = ContentType.objects.get_for_model(user)
        last_see_action = obj.action_object_actions.filter(
            actor_content_type=ct,
            actor_object_id=str(user.id),
            verb=settings.OPPORTUNITIES_ACT_ACTION_SEE).first()
        if not last_see_action:
            return obj.applicants.count()
        else:
            timestamp = last_see_action.timestamp
            return obj.applicants_info.filter(created__gte=timestamp).count()

    def get_questions(self, obj):
        questions = obj.questions.all().order_by('id')
        return QuestionSerializer(questions, many=True).data

    def get_requestedBy(self, obj):
        if obj.is_draft:
            user = obj.user_created_by
        else:
            user = obj.requested_by
        return OpportunityStatusSerializer(user).data

    def get_users_tagged(self, obj):
        response = []
        for user_tagged in obj.users_tagged.all():
            user = user_tagged.user
            user_wrapper = UserWrapper(user=user)
            response.append(UserSerializer(user_wrapper).data)
        return response

    def get_files(self, obj):
        return UploadedFileRelatedGenericSerializer(
            obj.files.all(), many=True, context=self.context).data

    def get_info_detail(self, obj):
        if obj.group:
            return obj.group.info_detail
        return obj.context_info_detail
