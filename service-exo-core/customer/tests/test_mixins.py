from ..faker_factories import FakeCustomerFactory


class TestCustomerMixin():

    def create_customer(self):
        self.customer = FakeCustomerFactory.create()
        return self.customer
