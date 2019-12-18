from django.conf import settings

from rest_framework import serializers

from keywords.serializers import KeywordSerializer
from languages.serializers import LanguageSerializer
from keywords.models import Keyword
from languages.models import Language
from exo_role.models import ExORole, CertificationRole
from files.api.serializers.uploaded_file import UploadedFileSerializer

from ...models import Opportunity, Applicant, OpportunityGroup
from .mixin import OpportunityUserMixin, OpportunityMixin
from .question import QuestionSerializer
from .answer import AnswerSerializer
from .opportunity_budget import BudgetSerializer
from .user import UserTaggedSerializer


class OpportunitySerializer(
        OpportunityMixin,
        OpportunityUserMixin,
        serializers.ModelSerializer):

    userBy = serializers.SerializerMethodField()
    keywords = KeywordSerializer(many=True, required=False)
    languages = LanguageSerializer(many=True, required=False)
    userStatus = serializers.SerializerMethodField()
    userActions = serializers.SerializerMethodField()
    numApplicants = serializers.SerializerMethodField()
    alreadyVisited = serializers.SerializerMethodField()
    isNew = serializers.SerializerMethodField()
    questions = QuestionSerializer(many=True, required=False)
    comment = serializers.CharField(
        required=False, allow_null=True, allow_blank=True,
    )
    send_notification = serializers.BooleanField(
        required=False)
    budgets = BudgetSerializer(required=False, many=True)
    users_tagged = UserTaggedSerializer(
        required=False, many=True)
    duration_unity = serializers.ChoiceField(
        required=False,
        choices=settings.OPPORTUNITIES_DURATION_UNITY_CHOICES)
    duration_value = serializers.IntegerField(required=False)
    exo_role = serializers.SlugRelatedField(
        queryset=ExORole.objects.all(),
        slug_field='code',
        required=True)
    certification_required = serializers.SlugRelatedField(
        queryset=CertificationRole.objects.all(),
        slug_field='code',
        required=False,
        allow_null=True)
    files = UploadedFileSerializer(many=True, required=False)
    group = serializers.PrimaryKeyRelatedField(
        queryset=OpportunityGroup.objects.all(),
        required=False)

    class Meta:
        model = Opportunity
        fields = [
            'pk', 'slug', 'uuid',
            'comment', 'send_notification',
            'title', 'description', 'keywords', 'languages',
            'mode', 'location', 'place_id', 'location_url',
            'start_date', 'modified',
            'entity',
            'exo_role', 'certification_required', 'other_role_name',
            'userStatus', 'userBy', 'other_category_name',
            'budgets',
            'alreadyVisited', 'isNew',
            'userActions', 'numApplicants',
            'questions',
            'num_positions', 'deadline_date',
            'users_tagged', 'target',
            'duration_unity', 'duration_value',
            'files', 'group',
            'context_object_uuid', 'context_content_type',
        ]
        read_only_fields = ['slug', 'modified', 'uuid']
        extra_kwargs = {
            'description': {
                'allow_blank': False,
                'required': True,
                'allow_null': False,
            },
        }

    def validate(self, data):
        action = self.context.get('view').action
        group = data.get('group')
        user = self.context.get('request').user

        if action == 'update':
            opportunity = self.context.get('view').get_object()
            can_update_opportunity = opportunity.can_do_actions(
                user, settings.OPPORTUNITIES_ACTION_CH_EDIT)
            if not can_update_opportunity:
                raise serializers.ValidationError("You can't update this opportunity")
        if group:
            if action in ['create', 'preview']:
                previous_opp = None
            else:
                previous_opp = self.instance
            position_availables = group.has_positions_availables(
                data.get('num_positions'),
                previous_opp,
            )
            if not position_availables:
                raise serializers.ValidationError("No positions availables")

        if 'other_category_name' not in data and \
                data['exo_role'].categories.first().code == settings.EXO_ROLE_CATEGORY_OTHER:
            raise serializers.ValidationError(
                detail='Other Category name is required')

        if 'other_category_name' in data and data['other_category_name'] and \
                data['exo_role'].categories.first().code != settings.EXO_ROLE_CATEGORY_OTHER:
            raise serializers.ValidationError(
                detail='Invalid Category')

        return data

    def create(self, validated_data):
        keywords = Keyword.objects.update_keywords(
            user_from=validated_data.get('user_from'),
            keywords_name=[k['name'] for k in validated_data.get('keywords')],
        )
        validated_data['keywords'] = keywords
        languages = Language.objects.update_languages(
            user_from=validated_data.get('user_from'),
            languages_name=set([k['name'] for k in validated_data.get('languages', [])]),
        )
        validated_data['languages'] = languages
        validated_data['users_tagged'] = [u['user'] for u in validated_data.get('users_tagged', [])]
        group = validated_data.pop('group', None)
        if group:
            return Opportunity.objects.create_opportunity_in_group(
                user_from=validated_data.pop('user_from'),
                group=group,
                **validated_data
            )
        else:
            return Opportunity.objects.create_opportunity(
                user_from=validated_data.pop('user_from'),
                **validated_data
            )

    def add_id_to_questions(self, validated_data):
        validated_data['questions'] = self.initial_data.get('questions')

    def update(self, instance, validated_data):
        keywords = Keyword.objects.update_keywords(
            user_from=validated_data.get('user_from'),
            keywords_name=[k['name'] for k in validated_data.get('keywords')],
        )
        validated_data['keywords'] = keywords
        languages = Language.objects.update_languages(
            user_from=validated_data.get('user_from'),
            languages_name=set([k['name'] for k in validated_data.get('languages', [])]),
        )
        validated_data['languages'] = languages
        self.add_id_to_questions(validated_data)
        validated_data['users_tagged'] = [u['user'].uuid for u in validated_data.get('users_tagged', [])]
        opportunity = Opportunity.objects.update_opportunity(
            user_from=validated_data.pop('user_from'),
            opportunity=instance,
            **validated_data)
        instance.refresh_from_db()
        return opportunity


class ApplyOpportunitySerializer(serializers.ModelSerializer):
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True)
    questions_extra_info = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True)
    budget = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True)
    answers = AnswerSerializer(many=True, required=False)

    class Meta:
        model = Opportunity
        fields = ['id', 'comment', 'questions_extra_info', 'budget', 'answers']

    def validate(self, data):
        opportunity = self.context['view'].get_object()
        if opportunity.questions.exists():
            try:
                assert data.get('answers')
                assert len(data.get('answers')) == opportunity.questions.count()
                for answer in data.get('answers'):
                    question = answer['question']
                    if question.is_boolean:
                        assert answer['response'].capitalize() in ['True', 'False']
            except AssertionError:
                raise serializers.ValidationError('Please answer questions')

        opportunity.can_apply(self.context.get('request').user)
        return data

    def update(self, instance, validated_data):
        Applicant.objects.create_open_applicant(
            user_from=validated_data.get('user_from'),
            user=validated_data.get('user_from'),
            opportunity=self.instance,
            summary=validated_data.get('comment'),
            questions_extra_info=validated_data.get('questions_extra_info'),
            budget=validated_data.get('budget'),
            answers=validated_data.get('answers', [])
        )
        return self.instance


class OpportunityReOpenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = ['deadline_date']
