from django.test import RequestFactory

from graphene.test import Client

from service.schema import schema


class GraphqlTestMixin:

    def _execute_query(self, query, variables, user):
        request_factory = RequestFactory()
        my_request = request_factory.get('/api/')
        my_request.user = user
        client = Client(schema)
        executed = client.execute(
            query,
            context_value=my_request,
            variable_values=variables,
        )
        return executed
