import os

IS_PRODUCTION = eval(os.environ.get('IS_PRODUCTION', 'False'))


if IS_PRODUCTION:
    GENERIC_TYPEFORMS = {
        'exo_certification_certification_quiz_en': 'm23mE5',
        'exo_certification_certification_quiz_es': 'H6Tzzu',
        'exo_certification_certification_assessment_en': 'H0mEnJ',
        'exo_certification_certification_assessment_es': 'mqasFi',
        'exo_certification_teaching_assignment_en': 'teachExOF',
        'exo_certification_teaching_assignment_es': 'teachExOFEs',
        'exo_certification_feedback_en': 'MIp7eA',
        'exo_certification_feedback_es': 'kh9K5N',
    }
else:
    GENERIC_TYPEFORMS = {
        'exo_certification_certification_quiz_en': 'rWYJUk',
        'exo_certification_certification_quiz_es': 'fVuCwb',
        'exo_certification_certification_assessment_en': 'cg9q8h',
        'exo_certification_certification_assessment_es': 'cfdLM0',
        'exo_certification_teaching_assignment_en': 'teachExOF',
        'exo_certification_teaching_assignment_es': 'teachExOFEs',
        'exo_certification_feedback_en': 'JibTBo',
        'exo_certification_feedback_es': 'zq0aPG',
    }

TYPEFORMFEEDBACK_VALIDATION_TEMPLATE = 'typeform/validate_typeform_response.html'
TYPEFORMFEEDBACK_NOTIFY_EMAILS_LIST = os.environ.get(
    'TYPEFORMFEEDBACK_NOTIFY_EMAILS_LIST',
    'qa@openexo.com',
).split(',')
