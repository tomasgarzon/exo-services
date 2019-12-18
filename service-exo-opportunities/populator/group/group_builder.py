from populate.populator.builder import Builder

from exo_role.models import ExORole, CertificationRole

from opportunities.models import OpportunityGroup


class GroupBuilder(Builder):

    def create_object(self):
        opportunity_group = OpportunityGroup.objects.create(
            uuid=self.data.get('uuid'),
            origin=self.data.get('origin'),
            related_uuid=self.data.get('related_uuid'),
            total=self.data.get('total'),
            exo_role=ExORole.objects.get(code=self.data.get('exo_role')),
            certification_required=CertificationRole.objects.get(code=self.data.get('certification_required')),
            duration_unity=self.data.get('duration_unity'),
            duration_value=self.data.get('duration_value'),
            entity=self.data.get('entity'),
            budgets=self.data.get('budgets'),
        )
        self.add_users(opportunity_group, self.data.get('managers', []))
        return opportunity_group

    def add_users(self, opportunity_group, managers):
        for manager in managers:
            opportunity_group.managers.add(manager['user'])
