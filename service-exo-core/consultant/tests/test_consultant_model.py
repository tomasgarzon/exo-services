from django.test import tag

from django.test import TestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from service.schema import schema
from utils.faker_factory import faker
from registration.models import RegistrationProcess
from core.models import Language

from ..models import Consultant
from ..faker_factories import FakeConsultantFactory
from ..search import consultant_settings


@tag('sequencial')
class ConsultantModelTest(SuperUserTestMixin, TestCase):

    def setUp(self):
        self.create_superuser()

    def test_status(self):
        c = FakeConsultantFactory.create()
        self.assertEqual(c.status_detail, consultant_settings.CH_CERTIFIED)

    def test_disable(self):
        c = FakeConsultantFactory.create()
        c.disable(self.super_user)
        c = Consultant.all_objects.get(id=c.id)
        self.assertTrue(c.is_disabled)
        self.assertEqual(c.status_detail, consultant_settings.CH_DISABLED)

    def test_graphql_consultant_by_email(self):
        email = faker.email()
        c = FakeConsultantFactory.create(
            user__email=email,
            status='A',
        )
        query = """query MiConsultor($email: String){
            allConsultants(user_Email: $email){
                edges {
                    node {
                        pk,
                        status,
                        modified
                    }
                }
            }
        }"""
        variables = {'email': email}
        result = schema.execute(query, variable_values=variables)
        consultant = result.data['allConsultants']['edges'][0]['node']
        self.assertEqual(consultant['status'], 'A')
        self.assertEqual(consultant['pk'], str(c.id))

    def test_graphql_consultant_registered(self):
        email = faker.email()
        c = FakeConsultantFactory.create(user__email=email)
        RegistrationProcess._create_process(
            self.super_user,
            c.user,
        )
        query = """
            query MiQuery($email: String){
              allConsultants(user_Email: $email) {
                edges {
                  node {
                    pk
                    languages {
                      edges {
                        node {
                          pk
                          name
                        }
                      }
                    }
                    user {
                      fullName
                      shortName
                      email
                      invitations {
                        edges {
                          node {
                            invStatus
                            invType
                          }
                        }
                      }
                    }
                    status
                  }
                }
              }
            }
        """
        c.languages.add(Language.objects.all()[0])
        c.languages.add(Language.objects.all()[1])
        variables = {'email': email}
        result = schema.execute(query, variable_values=variables)
        consultant = result.data['allConsultants']['edges'][0]['node']
        self.assertEqual(consultant['status'], 'P')
        self.assertEqual(consultant['pk'], str(c.id))
        self.assertEqual(len(consultant['languages']['edges']), 2)
