from django.utils import timezone

from utils.dates import string_to_datetime

JOB_CH_STATUS_UNSTARTED = 'UP'
JOB_CH_STATUS_FINISHED = 'CO'
JOB_CH_STATUS_RUNNING = 'IN'
JOB_CH_STATUS_UNSTARTED = 'UP'
JOB_CH_STATUS_UNKNOWN = 'UN'


def get_data_job_status(participant):
    now = timezone.now().date()
    status = JOB_CH_STATUS_UNKNOWN
    start = participant.event.start
    end = participant.event.end

    if (start and end) and start <= now <= end:
        status = JOB_CH_STATUS_RUNNING
    elif end and end < now:
        status = JOB_CH_STATUS_FINISHED
    elif start:
        if start > now:
            status = JOB_CH_STATUS_UNSTARTED
        else:
            status = JOB_CH_STATUS_RUNNING

    return status


def data_job_for_participant(participant):
    start_date = participant.event.start
    end_date = participant.event.end

    if start_date is None or end_date is None:
        return {}

    data = {
        'user': participant.user.uuid.__str__(),
        'related_class': 'CE',
        'related_uuid': participant.event.uuid.__str__(),
        'category': participant.category.code,
        'exoRole': participant.exo_role.code,
        'title': participant.event.title,
        'start': string_to_datetime(str(participant.event.start)).isoformat(),
        'end': string_to_datetime(str(participant.event.end)).isoformat(),
        'url': participant.event.url,
        'status': get_data_job_status(participant),
    }

    return data
