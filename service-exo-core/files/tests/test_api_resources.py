from django.urls import reverse
from django.conf import settings

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from utils.faker_factory import faker

from ..faker_factories import FakeResourceFileFactory, FakeResourceLinkFactory
from ..models import Resource  # noqa


class TestAPIResources(SuperUserTestMixin, DjangoRestFrameworkTestCase):
    def setUp(self):
        self.create_superuser()

    def test_api_get(self):
        FakeResourceLinkFactory.create_batch(size=3)
        FakeResourceFileFactory.create_batch(size=2)

        self.client.login(username=self.super_user.username, password='123456')
        url = reverse('api:file:resource-list')
        response = self.client.get(url, format='json')
        self.assertEqual(len(response.data), 5)
        response = self.client.get(
            url,
            data={'tags__name': settings.FILES_GENERAL_TAG},
            format='json',
        )
        self.assertEqual(len(response.data), 5)

    def test_add_tag(self):
        resource = FakeResourceLinkFactory.create()
        resource_id = resource.pk
        self.client.login(username=self.super_user.username, password='123456')
        url = reverse('api:file:resource-tag-add', kwargs={'pk': resource_id})
        data = {'name': faker.word() + faker.numerify()}
        self.client.put(
            url,
            data=data,
            format='json',
        )
        resource.refresh_from_db()
        self.assertTrue(data['name'] in resource.tags.all())

    def test_remove_tag(self):
        resource = FakeResourceLinkFactory.create()
        tag_name = faker.word() + faker.numerify()
        resource.tags.add(tag_name)
        resource_id = resource.pk
        self.client.login(username=self.super_user.username, password='123456')
        url = reverse('api:file:resource-tag-remove', kwargs={'pk': resource_id})
        data = {'name': tag_name}
        self.client.put(
            url,
            data=data,
            format='json',
        )
        resource.refresh_from_db()
        self.assertFalse(tag_name in resource.tags.all())
