from django.conf import settings

from ..mixins import ExternalServiceMixin
from ..urls import reverse


class MediaLibraryServiceWrapper(ExternalServiceMixin):
    host = settings.MEDIA_LIBRARY_HOST
    resources_url = reverse('media-library-resource-list')
    resources_project_url = reverse('media-library-resource-project-list')
    resources_auto_project = reverse('media-library-post-save-project')
    resources_delete_route = 'remove-from-projects'
    resources_add_route = 'add-to-projects'

    def get_resources(self, user_from, page, page_size):
        """
        List resources from medialibrary
        """
        url = '{}/?page={}&page_size={}'.format(
            self.resources_url,
            page,
            page_size)
        return self._do_request(url)

    def get_project_resources(self, user_from, page, page_size, uuid):
        """
        List resources from medialibrary assigned to the project uuid
        """
        url = '{}/?page={}&page_size={}&projects={}'.format(
            self.resources_project_url,
            page,
            page_size,
            uuid)
        return self._do_request(url)

    def add_resource_to_project(self, resource_pk, project, user_from):
        """
        Add resource from medialibrary to project library
        """
        url = '{}/{}/{}/'.format(
            self.resources_url,
            resource_pk,
            self.resources_add_route)

        data = {
            'uuid': project.uuid.hex,
        }

        return self._do_request_put(url, data)

    def remove_resource(self, resource_pk, project, user_from):
        """
        Remove resource from project library
        """
        url = '{}/{}/{}/'.format(
            self.resources_url,
            resource_pk,
            self.resources_delete_route)
        data = {
            'uuid': project.uuid.hex,
        }
        return self._do_request_put(url, data)

    def auto_assign_medialibrary_resources(self, project):
        """
        Auto creation project library
        """
        url = '{}/'.format(self.resources_auto_project)
        data = {
            'uuid': project.uuid.hex,
            'template': project.content_template,
        }
        return self._do_request_post(url, data)


medialibrary_wrapper = MediaLibraryServiceWrapper()
