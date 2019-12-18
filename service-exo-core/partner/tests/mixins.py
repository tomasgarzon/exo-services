from ..faker_factories import FakePartnerFactory


class TestPartnerMixin():

    def create_partner(self):
        self.partner = FakePartnerFactory.create()
        return self.partner
