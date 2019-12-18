from appconf import AppConf

from django.conf import settings  # noqa


class ValidationConfig(AppConf):

    CH_WARNING = 'W'
    CH_ERROR = 'E'

    CH_TYPE = (
        (CH_WARNING, 'Warning'),
        (CH_ERROR, 'Error'),
    )

    CH_PENDING = 'P'
    CH_FIXED = 'F'

    CH_STATUS = (
        (CH_PENDING, 'Pending'),
        (CH_FIXED, 'Fixed'),
    )

    CH_NO_TEAM = 'NT'
    CH_NO_ZOOM = 'NZ'
    CH_PART_PASS = 'PP'
    CH_NO_SURVEY = 'NS'
    CH_NO_EXQ = 'NQ'
    CH_NO_DATE = 'NC'
    CH_NO_MANAGER = 'NM'
    CH_ASSIGNMENT_PRIVATE = 'AP'
    CH_ASSIGNMENT_NO_DAY = 'AN'
    CH_ASSIGNMENT_STEP = 'AS'
    CH_NO_START = 'NA'
    CH_NO_CITY = 'NY'
    CH_NO_AGENDA = 'NG'
    CH_FASTRACK_TYPE = 'FT'
    CH_PERIOD_1_NO_START_DATE = 'PD'
    CH_SPRINT_AUTOMATED_MICROLEARNINGS = 'SM'
    CH_SPRINT_AUTOMATED_FEEDBACKS = 'SS'
    CH_STEPS_DEFINED = 'ST'

    LABEL_ERROR_NO_TEAM = 'There is no team created'
    LABEL_ERROR_NO_ZOOM = 'There is no Zoom API Key'
    LABEL_ERROR_NO_SURVEY = 'There is some team without ExQ Assessment'
    LABEL_WARNING_PARTICIPANT_PASSWORD = 'You should fix a default password for participants'
    LABEL_WARNING_EXQ = 'You should setup a ExQ Assessment'
    LABEL_ERROR_NO_DATE = 'Creation date before {}'
    LABEL_ERROR_NO_MANAGER = 'There is no {}'
    LABEL_WARNING_ASSIGNMENT_PRIVATE = 'There are some assignments not marked as public'
    LABEL_WARNING_ASSIGNMENT_NO_DAY = 'There are some assignments without day'
    LABEL_ERROR_START_DATE = 'The project needs a start date'
    LABEL_ERROR_CITY = 'The project needs a city/country'
    LABEL_WARNING_AGENDA = 'The project needs an agenda'
    LABEL_FASTRACK_TYPE = 'Fastrack sprint not supported yet'
    LABEL_WARNING_PERIOD_1_NO_START_DATE = 'Periods should have start date defined'
    LABEL_SPRINT_AUTOMATED_MICROLEARNINGS = 'Microlearnings must be defined from period Discover to Launch'
    LABEL_SPRINT_AUTOMATED_FEEDBACKS = 'Feedbacks must be defined from period Discover to Launch'
    LABEL_CH_ASSIGNMENT_STEP = 'Assignment steps should be defined for each step'
    LABEL_CH_STEPS_DEFINED = 'At least one step must be defined'

    VALIDATION_CH_DETAIL = (
        (CH_NO_TEAM, 'No team'),
        (CH_NO_ZOOM, 'No Zoom'),
        (CH_PART_PASS, 'Password default'),
        (CH_NO_SURVEY, 'No survey'),
        (CH_NO_EXQ, 'No ExQ'),
        (CH_NO_DATE, 'No date'),
        (CH_NO_MANAGER, 'No head coach/trainer'),
        (CH_ASSIGNMENT_PRIVATE, 'Assignments private'),
        (CH_ASSIGNMENT_NO_DAY, 'Assignment without day'),
        (CH_NO_START, 'Project not start'),
        (CH_NO_CITY, 'Project not city'),
        (CH_NO_AGENDA, 'Project not agenda'),
        (CH_FASTRACK_TYPE, 'Fastrack sprint not supported yet'),
    )

    LABEL_VALIDATION = {
        CH_NO_TEAM: LABEL_ERROR_NO_TEAM,
        CH_NO_ZOOM: LABEL_ERROR_NO_ZOOM,
        CH_PART_PASS: LABEL_WARNING_PARTICIPANT_PASSWORD,
        CH_NO_SURVEY: LABEL_ERROR_NO_SURVEY,
        CH_NO_EXQ: LABEL_WARNING_EXQ,
        CH_NO_DATE: LABEL_ERROR_NO_DATE,
        CH_NO_MANAGER: LABEL_ERROR_NO_MANAGER,
        CH_ASSIGNMENT_NO_DAY: LABEL_WARNING_ASSIGNMENT_NO_DAY,
        CH_ASSIGNMENT_PRIVATE: LABEL_WARNING_ASSIGNMENT_PRIVATE,
        CH_ASSIGNMENT_STEP: LABEL_CH_ASSIGNMENT_STEP,
        CH_NO_START: LABEL_ERROR_START_DATE,
        CH_NO_CITY: LABEL_ERROR_CITY,
        CH_NO_AGENDA: LABEL_WARNING_AGENDA,
        CH_FASTRACK_TYPE: LABEL_FASTRACK_TYPE,
        CH_PERIOD_1_NO_START_DATE: LABEL_WARNING_PERIOD_1_NO_START_DATE,
        CH_SPRINT_AUTOMATED_MICROLEARNINGS: LABEL_SPRINT_AUTOMATED_MICROLEARNINGS,
        CH_SPRINT_AUTOMATED_FEEDBACKS: LABEL_SPRINT_AUTOMATED_FEEDBACKS,
        CH_STEPS_DEFINED: LABEL_CH_STEPS_DEFINED,
    }

    ONLY_STAFF = [CH_NO_ZOOM]
