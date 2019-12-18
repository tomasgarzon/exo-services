from django import test

from graphql import parse

from ..graphene.document_ast import ast_depth


class GraphqlTest(test.TestCase):

    def test_depth_query_projects(self):
        # PREPARE DATA
        query = """query allProject {
          allProject {
            edges {
              node {
                firstDay
                lastDay
                name
                typeProject
                nextUrl
                adminUrl
                timezone
                allowedAccess
                projectIncidences
                __typename
              }
              __typename
            }
            __typename
          }
        }
        """

        # DO ACTION
        document_ast = parse(query)
        depth = ast_depth(document_ast.definitions[0])

        # ASSERTS
        self.assertEqual(depth, 2)

    def test_depth_query_opportunities(self):
        # PREPARE DATA
        query = """query myOpportunities {
          myOpportunities {
            edges {
              node {
                pk
                subject
                userStatus
                dueDate
                target
                modified
                userBy
                project {
                  name
                  timezone
                  __typename
                }
                myApplicant {
                  pk
                  timezone
                  consultant {
                    pk
                    __typename
                  }
                  dialogItems {
                    totalCount
                    __typename
                  }
                  slots {
                    edges {
                      node {
                        pk
                        status
                        when
                        timezone
                        __typename
                      }
                      __typename
                    }
                    __typename
                  }
                  __typename
                }
                __typename
              }
              __typename
            }
            __typename
          }
        }
        """
        # DO ACTION
        document_ast = parse(query)
        depth = ast_depth(document_ast.definitions[0])

        # ASSERTS
        self.assertEqual(depth, 4)
