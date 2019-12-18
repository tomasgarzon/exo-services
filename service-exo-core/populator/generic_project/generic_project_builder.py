import uuid

from django.conf import settings

from generic_project.faker_factories import GenericProjectFactory
from populate.populator.common.helpers import find_tuple_values
from consultant.models import Consultant

from ..sprint_automated.project_builder import ProjectBuilder


class GenericProjectBuilder(ProjectBuilder):

    def create_project(self):
        category = find_tuple_values(
            settings.PROJECT_CH_CATEGORY,
            self.data.get('category', 'Transformation')
        )[0]
        generic_project = GenericProjectFactory(
            id=self.data.get('id'),
            uuid=self.data.get('uuid', uuid.uuid4()),
            name=self.data.get('name'),
            customer=self.data.get('customer'),
            duration=self.data.get('duration'),
            category=category,
            lapse=settings.PROJECT_LAPSE_PERIOD,
            start=self.data.get('start'),
            location=self.data.get('place').get('name'),
            place_id=self.data.get('place').get('place_id'),
        )

        user = self.data.get('created_by')
        if user and isinstance(user, Consultant):
            generic_project.created_by = user.user
        else:
            generic_project.created_by = user
        if self.data.get('template'):
            generic_project.template = self.data.get('template')
        generic_project.save()
        return generic_project

    def update_steps(self, project):
        for stp in self.data.get('steps', []):
            step = project.steps.get(index=stp.get('order'))
            step.name = stp.get('name')
            step.save()
