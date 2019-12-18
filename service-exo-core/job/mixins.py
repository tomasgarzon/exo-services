from .models import CoreJob
from .tasks import CoreJobUpdate


class JobMixin:

    def get_items_related(self):
        classname = self.__class__.__name__.lower()
        items_related = []

        if classname == 'project':
            c_project_roles = self.consultants_roles.all().actives_only()
            u_project_roles = self.users_roles.all().actives_only()
            items_related = list(c_project_roles) + list(u_project_roles)

        elif classname == 'qasession':
            items_related = list(self.qa_session_advisors.all())

        return items_related

    def delete_related_jobs(self):
        items_related = self.get_items_related()

        for instance in items_related:
            CoreJob.objects.all().filter_by_instance(instance).delete()

    def update_related_jobs(self):
        items_related = self.get_items_related()

        for instance in items_related:
            core_jobs_for_instance = CoreJob.objects.all().filter_by_instance(instance)

            if core_jobs_for_instance.exists():
                for core_job in core_jobs_for_instance:
                    CoreJobUpdate().s(job_id=core_job.id).apply_async()
            else:
                if instance.need_job:
                    CoreJob.objects.create_from_instance(instance)
                else:
                    CoreJob.objects.all().filter_by_instance(instance).delete()
