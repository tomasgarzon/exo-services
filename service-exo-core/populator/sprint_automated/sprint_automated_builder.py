from datetime import timedelta
import uuid

from django.conf import settings

from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from consultant.models import Consultant
from .project_builder import ProjectBuilder


class SprintAutomatedBuilder(ProjectBuilder):

    def create_project(self):
        sprint = FakeSprintAutomatedFactory(
            id=self.data.get('id'),
            uuid=self.data.get('uuid', uuid.uuid4()),
            name=self.data.get('name'),
            customer=self.data.get('customer'),
            duration=settings.SPRINT_AUTOMATED_STEPS_COUNT,
            lapse=settings.PROJECT_LAPSE_PERIOD,
            start=self.data.get('start'),
            location=self.data.get('place').get('name'),
            place_id=self.data.get('place').get('place_id'),
        )

        user = self.data.get('created_by')
        if user and isinstance(user, Consultant):
            sprint.created_by = user.user
        else:
            sprint.created_by = user
        sprint.save()
        return sprint

    def update_steps(self, project):
        lapse = {'{}s'.format(self.data.get('lapse', 'Week').lower()): 1}
        initial_date = project.start + timedelta(**lapse)
        final_date = initial_date + timedelta(**lapse)
        for period in project.steps.all():
            period.start = initial_date
            period.end = final_date
            period.save()
            initial_date = final_date + timedelta(minutes=1)
            final_date = final_date + timedelta(**lapse)
