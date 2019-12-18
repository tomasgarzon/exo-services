from django.test import TestCase

from mock import patch

from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from utils.faker_factory import faker


class TestHubspotContact(TestCase):

    @patch('consultant.tasks.hubspot_integrations.HubspotUpdateContactEmailTask.apply_async')
    def test_update_contact_email_at_hubspot(self, hubspot_sync_patch):
        # PREPARE DATA
        user = FakeUserFactory.create()
        email_address = user.add_email_address(faker.email().upper())

        # DO ACTION
        email_address._set_primary_flags()

        # ASSERTIONS
        self.assertTrue(hubspot_sync_patch.called)
