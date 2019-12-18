from django.test import TestCase

from test_utils.test_case_mixins import SuperUserTestMixin
from test_utils.graphql_test_mixin import GraphqlTestMixin
from project.signals_define import project_post_launch

from .test_mixins import TestProjectMixin
from ..conf import settings


class ProjectGraphqlTest(
        SuperUserTestMixin,
        GraphqlTestMixin,
        TestProjectMixin,
        TestCase):

    def setUp(self):
        self.create_superuser()
        self.receivers = project_post_launch.receivers.copy()
        project_post_launch.receivers = []

    def tearDown(self):
        project_post_launch.receivers = self.receivers

    def _execute_project_query(self, project, user):
        query = """query allProject($pk: String) {
          allProject(pk: $pk) {
            edges {
              node {
                steps {
                  edges {
                    node {
                      index
                      streams {
                        edges {
                          node {
                            stream
                            userTypeformFeedback{
                              url
                              status
                            }
                            typeformFeedback{
                              edges{
                                node{
                                  typeformUrl
                                  typeformType
                                  responses{
                                    edges{
                                      node{
                                        status
                                        url
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
                  }
                }
              }
            }
          }
        }"""

        project.launch(self.super_user)
        return self._execute_query(
            query=query,
            variables={'pk': str(project.pk)},
            user=user)

    def test_participant_feedback_steps(self):
        sprint, _, _ = self._build_sprint()
        project = sprint.project_ptr
        participant = project.teams.first().team_members.first()
        executed = self._execute_project_query(project, participant)
        steps = executed['data']['allProject']['edges'][0]['node']['steps']['edges']
        for step in steps:
            step_index = step['node']['index']
            streams = step['node']['streams']['edges']
            for stream in streams:
                if stream['node']['stream'] == project.teams.first().stream:
                    step_stream = stream['node']
                    break
            if step_index == 1:
                self.assertIsNone(step_stream['userTypeformFeedback'])
            else:
                self.assertEqual(
                    step_stream['userTypeformFeedback']['status'],
                    settings.TYPEFORM_FEEDBACK_USER_FEEDBACK_STATUS_PENDING,
                )

    def test_coach_feedback_steps(self):
        sprint, _, _ = self._build_sprint()
        project = sprint.project_ptr
        coach = project.teams.first().coach
        executed = self._execute_project_query(project, coach.user)
        steps = executed['data']['allProject']['edges'][0]['node']['steps']['edges']

        for step in steps:
            streams = step['node']['streams']['edges']
            for stream in streams:
                if stream['node']['stream'] == project.teams.first().stream:
                    step_stream = stream['node']
                    break

            self.assertIsNone(step_stream['userTypeformFeedback'])
