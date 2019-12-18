from rest_framework import serializers

from exo_role.api.serializers import ExORoleSerializer, CertificationRoleSerializer

from ...models import Opportunity
from .mixin import OpportunityMixin, OpportunityUserMixin
from .opportunity_budget import BudgetSerializer
from .applicant import OpportunityApplicantSerializer, OpportunityApplicantSimpleSerializer


class OpportunityListSerializer(
        OpportunityMixin,
        OpportunityUserMixin,
        serializers.ModelSerializer):
    numApplicants = serializers.SerializerMethodField()
    applicants = serializers.SerializerMethodField()
    num_messages = serializers.SerializerMethodField()
    alreadyVisited = serializers.SerializerMethodField()
    isNew = serializers.SerializerMethodField()
    userStatus = serializers.SerializerMethodField()
    userActions = serializers.SerializerMethodField()
    budgets = BudgetSerializer(many=True)
    status = serializers.CharField()
    exo_role = ExORoleSerializer()
    certification_required = CertificationRoleSerializer()

    class Meta:
        model = Opportunity
        fields = [
            'alreadyVisited', 'created', 'modified',
            'isNew', 'start_date', 'entity', 'pk',
            'mode', 'location', 'place_id', 'location_url',
            'applicants', 'numApplicants', 'num_messages',
            'exo_role', 'certification_required', 'title',
            'other_role_name', 'other_category_name',
            'status', 'userStatus', 'userActions', 'target',
            'num_positions', 'uuid', 'deadline_date',
            'budgets', 'duration_unity', 'duration_value',
            'has_been_edited',
        ]

    @property
    def is_admin_action(self):
        request = self.context.get('request')
        return request.GET.get('published_by_you') is not None

    def get_userActions(self, obj):
        return obj.user_actions(
            self.context.get('request').user,
            remove_admin_actions=not self.is_admin_action,
        )

    def get_num_messages(self, obj):
        return getattr(obj, 'num_messages', {})

    def get_applicants(self, obj):
        if self.is_admin_action:
            data = []
            queryset = obj.applicants_info.all().order_by_status()
            data.extend(
                OpportunityApplicantSerializer(
                    queryset[:4], many=True,
                    context=self.context).data
            )
            data.extend(
                OpportunityApplicantSimpleSerializer(
                    queryset[4:], many=True,
                    context=self.context).data)
            return data
        return []


class OpportunityBadgeListSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='exo_role.code')
    category = serializers.CharField(source='category.code')
    users = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
            'code',
            'category',
            'title',
            'start_date',
            'users',
        ]

    def get_users(self, obj):
        return obj.applicants_selected.values_list('user__uuid', flat=True)
