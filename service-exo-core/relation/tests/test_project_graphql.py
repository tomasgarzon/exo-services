from django.conf import settings

from exo_role.models import ExORole

from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from test_utils.graphql_test_mixin import GraphqlTestMixin
from test_utils import DjangoRestFrameworkTestCase
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from relation.faker_factories import FakeConsultantProjectRoleFactory, FakeUserProjectRoleFactory


class ProjectGraphqlTest(
        UserTestMixin,
        SuperUserTestMixin,
        GraphqlTestMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()

    def initialize_project(self):
        sprint = FakeSprintAutomatedFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        project = sprint.project_ptr
        role = FakeConsultantProjectRoleFactory.create(
            project=project,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            status=settings.RELATION_ROLE_CH_ACTIVE,
            consultant__user__is_active=True,
            consultant__user__password='123456',
        )
        FakeUserProjectRoleFactory.create(
            status=settings.RELATION_ROLE_CH_ACTIVE,
            project=project,
            user=self.user
        )

        query = """query allProject($pk: String) {
            allProject(pk: $pk) {
            edges {
                node {
                    consultantsRoles {
                        edges {
                            node {
                            rating
                            exoRole {
                                code
                                name
                            }
                    consultant {
                        pk
                        user {
                            pk
                            fullName
                            shortName
                            slug
                            isOpenexoMember
                            profilePictures {
                                width
                                height
                                url
                            }
                        }
                    }
                }
              }
            }
            usersRoles {
              edges {
                node {
                  status
                  exoRole {
                    code
                    name

                  }
                  user {
                    pk
                    fullName
                    shortName
                    slug
                    profilePictures {
                      width
                      height
                      url
                    }
                  }
                }
              }
            }
            teams {
              edges {
                node {
                  pk
                  name
                  coach {
                    pk
                  }
                  teamMembers {
                    edges {
                      node {
                        pk
                      }
                    }
                  }
                }
              }
                }
              }
            }
          }
        }
        """
        return project, query, role.consultant

    def test_consultant_project_role_rating(self):
        # PREPARE DATA
        project, query, consultant = self.initialize_project()
        variables = {'pk': str(project.pk)}

        # DO QUERY
        users = [
            self.super_user, consultant.user
        ]
        for user in users:
            executed = self._execute_query(query, variables, user)
            # ASSERTS
            roles = executed['data']['allProject']['edges'][0]['node']['consultantsRoles']['edges']
            self.assertEqual(len(roles), 1)

    def test_consultant_project_role_rating_user(self):
        # PREPARE DATA
        project, query, _ = self.initialize_project()
        variables = {'pk': str(project.pk)}

        # DO QUERY
        executed = self._execute_query(query, variables, self.user)

        # ASSERTS
        roles = executed['data']['allProject']['edges'][0]['node']['consultantsRoles']['edges']
        self.assertEqual(len(roles), 1)
        rating = roles[0]['node']['rating']
        self.assertIsNone(rating)
