from django.test import TestCase

from service.schema import schema

from ..models import Customer
from ..faker_factories import FakeCustomerFactory


class TestCustomerGraphQL(TestCase):

    def setUp(self):
        super().setUp()

    def test_customer_graphql(self):
        FakeCustomerFactory.create_batch(size=10)
        query = """
            query {
              allCustomers {
                edges {
                  node {
                    name
                    description
                    id
                  }
                }
              }
            }
        """
        result = schema.execute(query)
        self.assertEqual(
            len(result.data.get('allCustomers').get('edges')),
            10,
        )

    def test_customer_graphql_filter(self):
        FakeCustomerFactory.create_batch(size=10)
        query = """
            query MiQuery ($name: String){
              allCustomers (name: $name){
                edges {
                  node {
                    name
                    description
                    id
                  }
                }
              }
            }
        """
        customer = Customer.objects.last()
        variables = {'name': customer.name}
        result = schema.execute(query, variable_values=variables)
        self.assertEqual(
            len(result.data.get('allCustomers').get('edges')),
            1,
        )
