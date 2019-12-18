from dj_anonymizer.register_models import (
    AnonymBase,
    register_anonym,
    register_skip
)
from dj_anonymizer import anonym_field

from utils.faker_factory import faker

from opportunities import models


class OpportunityAnonym(AnonymBase):
    title = anonym_field.function(faker.sentence)
    description = anonym_field.function(faker.text)
    entity = anonym_field.function(faker.word)

    class Meta:
        exclude_fields = [
            '_status',
            'slug',
            'target',
            'uuid',
            'keywords',
            'mode',
            'location',
            'place_id',
            'location_url',
            'start_date',
            'deadline_date',
            'duration_unity',
            'duration_value',
            'budget',
            'budget_currency',
            'virtual_budget',
            'virtual_budget_currency',
            'applicants',
            'num_positions',
            'modified',
            'created',
            'created_by',
            'action_object_actions',
            'target_actions',
            'actor_actions',
            'sent_at',
            'exo_role',
            'certification_required',
            'other_role_name',
            'files',
            'other_category_name',
            'context_content_type', 'context_object_uuid',
        ]


class QuestionAnonym(AnonymBase):
    title = anonym_field.function(faker.sentence)

    class Meta:
        exclude_fields = [
            'opportunity',
            'type_question',
            'created',
            'modified',
        ]


class ApplicantAnonym(AnonymBase):
    summary = anonym_field.function(faker.text)
    questions_extra_info = anonym_field.function(faker.text)
    response_message = anonym_field.function(faker.text)

    class Meta:
        exclude_fields = [
            'user',
            'opportunity',
            'status',
            'budget',
            'created',
            'modified',
        ]


class AnswerAnonym(AnonymBase):

    class Meta:
        exclude_fields = [
            'applicant',
            'question',
            'response',
            'created',
            'modified',
        ]


register_anonym([
    (models.Opportunity, OpportunityAnonym),
    (models.Applicant, ApplicantAnonym),
    (models.Question, QuestionAnonym),
    (models.Answer, AnswerAnonym)
])

register_skip([models.OpportunityStatus])
