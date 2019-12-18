from django import test

from test_utils.test_case_mixins import SuperUserTestMixin

from ..faker_factories import FakeResourceFactory
from ..models import Resource


class TestResourceQuerysetTest(SuperUserTestMixin, test.TestCase):

    def setUp(self):
        self.create_superuser()

    def test_faker_factory(self):
        resource = FakeResourceFactory.create()

        self.assertIsNotNone(resource.name)
        self.assertIsNotNone(resource.file)
        self.assertIsNotNone(resource.link)
        self.assertTrue(resource.active)
        self.assertEqual(resource.order, 1)
        resource2 = FakeResourceFactory.create()
        self.assertEqual(resource2.order, 2)

    def test_resource_method(self):
        resource = FakeResourceFactory.create(link=None)

        self.assertTrue(resource.is_file)
        self.assertIsNotNone(resource.get_download_url())

    def test_resource_filter(self):
        FakeResourceFactory.create(active=True)
        FakeResourceFactory.create_batch(size=3, active=False)
        self.assertEqual(Resource.objects.actives().count(), 1)
        self.assertEqual(Resource.objects.count(), 4)
