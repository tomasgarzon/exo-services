from django.utils import timezone
from django.conf import settings

from utils.dates import string_to_datetime

JOB_CH_STATUS_UNSTARTED = 'UP'
JOB_CH_STATUS_FINISHED = 'CO'
JOB_CH_STATUS_RUNNING = 'IN'
JOB_CH_STATUS_UNSTARTED = 'UP'
JOB_CH_STATUS_UNKNOWN = 'UN'


def get_data_job_status(user_project_role):
    now = timezone.now().date()
    status = JOB_CH_STATUS_UNKNOWN
    start = user_project_role.project.start
    end = user_project_role.project.end

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


def data_job_for_user_project_role(user_project_role):
    start_date = user_project_role.project.start
    end_date = user_project_role.project.end
    project = user_project_role.project

    if start_date is None or end_date is None:
        return {}

    data = {
        'user': user_project_role.user.uuid.__str__(),
        'related_class': 'CX',
        'related_uuid': user_project_role.project.uuid.__str__(),
        'category': user_project_role.exo_role.categories.first().code,
        'exoRole': user_project_role.exo_role.code,
        'title': project.name,
        'start': string_to_datetime(str(start_date)).isoformat(),
        'end': string_to_datetime(str(end_date)).isoformat(),
        'url': user_project_role.url,
        'status': get_data_job_status(user_project_role),
    }

    try:
        current_step = project.steps.filter(
            status=settings.PROJECT_CH_STATUS_STEP_CURRENT).get().name
    except Exception:
        current_step = project.current_step().name

    data['status_detail'] = current_step

    return data
