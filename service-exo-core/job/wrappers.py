from django.utils import timezone

from exo_role.models import ExORole, Category

from project.helpers import next_project_url

from .conf import settings


class JobWrapper:
    user = None
    instance = None
    title = None
    start = None
    end = None
    category = None
    status = None
    status_detail = None
    exo_role = None
    url = None
    extra_data = None
    related_uuid = None
    related_class = 'CX'

    def __init__(self, instance, user, *args, **kwargs):
        self.instance = instance
        self.user = user

    @property
    def status(self):
        now = timezone.now()
        status = settings.JOB_CH_STATUS_UNKNOWN

        if (self.start and self.end) and self.start <= now <= self.end:
            if self.category.code == settings.EXO_ROLE_CATEGORY_SWARM:
                status = settings.JOB_CH_STATUS_LIVE
            else:
                status = settings.JOB_CH_STATUS_RUNNING
        elif self.end and self.end < now:
            status = settings.JOB_CH_STATUS_FINISHED
        elif self.start:
            if self.start > now:
                status = settings.JOB_CH_STATUS_UNSTARTED
            else:
                status = settings.JOB_CH_STATUS_RUNNING

        return status

    def dump_data(self):

        data = {
            'user': self.user.uuid.__str__(),
            'related_class': self.related_class,
            'related_uuid': self.related_uuid,
            'category': self.category.code,
            'exoRole': self.exo_role.code,
            'title': self.title,
            'start': self.start.isoformat(),
            'status': self.status,
            'extraData': self.extra_data,
        }

        if self.url:
            data['url'] = self.url

        if self.end:
            data['end'] = self.end.isoformat()

        if self.status_detail:
            data['status_detail'] = self.status_detail

        return data


class ProjectJob(JobWrapper):
    @property
    def related_uuid(self):
        return self.instance.project.uuid.__str__()

    @property
    def title(self):
        return self.instance.project.name

    @property
    def start(self):
        return self.instance.project.get_project_start_date()

    @property
    def end(self):
        return self.instance.project.get_project_end_date()

    @property
    def category(self):
        return self.instance.exo_role.categories.first()

    @property
    def exo_role(self):
        return self.instance.exo_role

    @property
    def url(self):
        url, _ = next_project_url(self.instance.project, self.user)
        return url

    @property
    def status_detail(self):
        status_detail = None

        if self.category.code == settings.EXO_ROLE_CATEGORY_EXO_SPRINT:
            project = self.instance.project
            current_step = project.current_step()

            if current_step:
                status_detail = current_step.name

        return status_detail


class FastrackJob(JobWrapper):
    @property
    def related_uuid(self):
        return self.instance.project.uuid.__str__()

    @property
    def title(self):
        return self.instance.project.name

    @property
    def start(self):
        return self.instance.project.get_project_start_date()

    @property
    def end(self):
        return self.instance.project.get_project_end_date()

    @property
    def category(self):
        return self.instance.exo_role.categories.first()

    @property
    def exo_role(self):
        return self.instance.exo_role


class QASessionAdvisorJob(JobWrapper):
    @property
    def related_uuid(self):
        return self.instance.qa_session.project.uuid.__str__()

    @property
    def title(self):
        return self.instance.qa_session.name

    @property
    def start(self):
        return self.instance.qa_session.start_at

    @property
    def end(self):
        return self.instance.qa_session.end_at

    @property
    def category(self):
        return Category.objects.get(code=settings.EXO_ROLE_CATEGORY_SWARM)

    @property
    def exo_role(self):
        return ExORole.objects.get(code=settings.EXO_ROLE_CODE_ADVISOR)

    @property
    def url(self):
        return settings.FRONTEND_JOBS_SWARM_PAGE.format(**{'pk': self.instance.qa_session.pk})
