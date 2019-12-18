from django.test import TestCase

from relation.faker_factories import FakeInternalOrganizationUserRoleFactory


class TestUserProfileWrapper(TestCase):

    def test_wrapper_user_title(self):
        # PREPARE DATA
        organization_user_role = FakeInternalOrganizationUserRoleFactory.create()

        inputs = [
            organization_user_role.user,
        ]
        outputs = [
            '{} at {}'.format(organization_user_role.position, organization_user_role.organization.name),
        ]

        # DO ACTION
        for index, user in enumerate(inputs):
            user_title = user.user_title

            # ASSERTS
            self.assertEqual(user_title, outputs[index])
