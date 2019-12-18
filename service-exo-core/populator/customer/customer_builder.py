from customer.faker_factories import FakeCustomerFactory
from industry.models import Industry

from populate.populator.builder import Builder


class CustomerBuilder(Builder):

    def create_object(self):
        return self.create_customer(
            name=self.data.get('name'),
            industry=self.data.get('industry'),
            website=self.data.get('website'),
            place=self.data.get('place'),
            timezone=self.data.get('timezone'))

    def create_customer(self, name, industry, website, place, timezone):
        customer = FakeCustomerFactory(
            name=name,
            industry=Industry.objects.get(name=industry),
            website=website,
            location=place.get('name'),
            place_id=place.get('place_id'),
            timezone=timezone)

        return customer
