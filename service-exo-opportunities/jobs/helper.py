from django.conf import settings

from utils.dates import string_to_datetime


def get_data_job_status(applicant):
    JON_CH_STATUS_UNSTARTED = 'UP'
    JOB_CH_STATUS_FINISHED = 'CO'

    mapping = {
        settings.OPPORTUNITIES_CH_APPLICANT_SELECTED: JON_CH_STATUS_UNSTARTED,
        settings.OPPORTUNITIES_CH_APPLICANT_COMPLETED: JOB_CH_STATUS_FINISHED,
        settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_REQUESTER: JOB_CH_STATUS_FINISHED,
        settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_APP: JOB_CH_STATUS_FINISHED,
        settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_READY: JOB_CH_STATUS_FINISHED,
    }
    return mapping.get(applicant.status or None)


def data_job_for_applicant(applicant):
    if not applicant.has_sow:
        return {}

    start_date = applicant.sow.start_date
    end_date = applicant.sow.end_date

    if start_date is None or end_date is None:
        return {}

    data = {
        'user': applicant.user.uuid.__str__(),
        'related_class': 'CO',
        'related_uuid': applicant.opportunity.uuid.__str__(),
        'category': applicant.opportunity.exo_role.categories.first().code,
        'exoRole': applicant.opportunity.exo_role.code,
        'title': applicant.opportunity.title,
        'start': string_to_datetime(str(applicant.sow.start_date)).isoformat(),
        'end': string_to_datetime(str(applicant.sow.end_date)).isoformat(),
        'url': applicant.url,
        'status': get_data_job_status(applicant),
    }
    if applicant.opportunity.is_online:
        data['extraData'] = {
            'url': applicant.opportunity.location_url
        }

    return data
