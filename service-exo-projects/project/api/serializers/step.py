from rest_framework import serializers

from utils.drf.project import CurrentProjectDefault
from assignment.api.serializers.assignment_step import AssignmentStepSerializer
from learning.api.serializers.personal_quiz import PersonalQuizSerializer

from .step_rating import Rating, RatingSerializer
from .step_feedback import StepFeedBackSummarySerializer
from ...models import Step
from ...helpers import get_feedback_summary
from ...signals_define import step_started_changed


class StepSerializer(serializers.ModelSerializer):
    project = serializers.HiddenField(
        default=CurrentProjectDefault())
    has_assignments = serializers.SerializerMethodField()

    class Meta:
        model = Step
        read_only_fields = ['status']
        fields = [
            'name', 'index', 'start', 'end', 'project', 'pk',
            'has_assignments', 'current', 'status']

    def get_has_assignments(self, obj):
        teams = {}
        for team in self.context.get('view').project.teams.all():
            teams[team.pk] = obj.has_team_assignments(team)
        return teams

    def update(self, instance, validated_data):
        step = super().update(instance, validated_data)
        step_started_changed.send(
            sender=step.__class__,
            instance=step)
        return step


class StepDetailSerializer(serializers.ModelSerializer):
    assignments = serializers.SerializerMethodField()
    personal_quiz = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()
    feedback_received = serializers.SerializerMethodField()
    step_conf = serializers.SerializerMethodField()
    deliverable_step_endpoint = serializers.SerializerMethodField()
    can_download = serializers.SerializerMethodField()

    class Meta:
        model = Step
        read_only_fields = ['status']
        fields = [
            'pk',
            'name',
            'start',
            'end',
            'assignments',
            'personal_quiz',
            'feedback',
            'feedback_received',
            'step_conf',
            'deliverable_step_endpoint',
            'index',
            'can_download',
            'status',
        ]

    def get_deliverable_step_endpoint(self, obj):
        """
        Get the `AssignmentStepTeam` pk identifier for this `Team` associated with
        the `Step`
        """
        endpoint = None
        team = self.context.get('view').team
        assignment_step = obj.assignments_step.filter_by_stream(
            team.stream).filter_by_step(obj)

        if assignment_step.exists():
            assignment_step_team = assignment_step.first().assignment_step_teams.filter(
                team=team).first()
            endpoint = assignment_step_team.pk
        return endpoint

    def get_assignments(self, obj):
        team = self.context.get('view').team
        items = obj.assignments_step.filter_by_stream(team.stream)
        return AssignmentStepSerializer(
            items,
            many=True,
            context=self.context).data

    def _get_microlearning(self, obj):
        microlearning = None
        team = self.context.get('view').team
        step_stream = obj.streams.filter(stream=team.stream).first()

        if hasattr(step_stream, 'microlearning'):
            microlearning = step_stream.microlearning

        return microlearning

    def get_personal_quiz(self, obj):
        personal_quiz = {}
        team = self.context.get('view').team
        user = self.context.get('request').user

        microlearning = self._get_microlearning(obj)
        if microlearning:
            user_microlearning, _ = microlearning.responses.get_or_create(
                user=user,
                team=team,
            )
            personal_quiz = PersonalQuizSerializer(user_microlearning).data

        return personal_quiz

    def _enabled_section(self, obj, section_name):
        enable_section = False
        assignment = obj.assignments_step.first()
        if assignment:
            enable_section = assignment.settings.get(section_name, False)
        return enable_section

    def _enabled_quiz(self, obj):
        microlearning = self._get_microlearning(obj)
        return microlearning and microlearning.typeform_url

    def get_step_conf(self, obj):
        return {
            'enabledLearn': self._enabled_section(obj, 'enabled_learn'),
            'enabledDeliver': self._enabled_section(obj, 'enabled_deliver'),
            'enabledReflect': self._enabled_section(obj, 'enabled_reflect'),
            'enabledQuiz': self._enabled_quiz(obj),
        }

    def get_feedback(self, obj):
        team = self.context.get('view').team
        user = self.context.get('request').user
        team_step = obj.teams.get(team=team)
        is_valid = team_step.check_user_can_rate(
            user, raise_exceptions=False)
        if is_valid:
            rating = Rating()
            rating.build_from_team_step(team_step, user)
            serializer = RatingSerializer(rating)
            feedback_conf = serializer.data
            return feedback_conf
        return None

    def get_feedback_received(self, obj):
        user_from = self.context.get('request').user
        team = self.context.get('view').team
        team_step = obj.teams.get(team=team)

        summary = get_feedback_summary(user_from, team_step)

        serializer = StepFeedBackSummarySerializer(summary, many=True)
        return serializer.data

    def get_can_download(self, obj):
        user_from = self.context.get('request').user
        return obj.can_download_report(user_from, raise_exceptions=False)
