from django.contrib.auth.models import Permission

from ...models import Resource, Category, Tag
from ...faker_factories import CategoryFactory, TagFactory, VideoFactory
from ...signals.define import post_save_resource_signal


class TestResourceMixin:

    def _create_video(self, link=None, modified=None):
        if link and modified:
            video_data = VideoFactory.create(
                link=link, modified=modified)
        else:
            video_data = VideoFactory.create()
        resource, created = Resource.objects.update_or_create(**video_data)
        post_save_resource_signal.send(sender=resource)
        return resource, created

    def _create_category(self, name=None):
        if name:
            category = CategoryFactory.create(name=name)
        else:
            category = CategoryFactory.create()
        categories = Category.objects.create_categories_vimeo([category])
        return categories[0]

    def _create_tag(self, name=None, commit=False):
        if name:
            tag = TagFactory.create(name=name)
        else:
            tag = TagFactory.create()
        tags = Tag.objects.create_tags_vimeo([tag])
        tag = tags[0]
        if commit:
            tag.save()
        return tag

    def _create_resources(self, resources):
        for resource_data in resources:
            resource, _ = Resource.objects.update_or_create(**resource_data)
            post_save_resource_signal.send(sender=resource)

    def _create_videos(self, num_videos):
        videos = VideoFactory.create_batch(size=num_videos)
        self._create_resources(videos)
        return videos

    def _create_categories(self, num_categories):
        categories = CategoryFactory.create_batch(
            size=num_categories)
        return Category.objects.create_categories_vimeo(categories)

    def _create_tags(self, num_tags):
        tags = TagFactory.create_batch(size=num_tags)
        return Tag.objects.create_tags_vimeo(tags)

    def _add_categories_to_resource(self, categories, resource):
        return Category.objects.add_categories_to_resource(categories, resource)

    def _add_tags_to_resource(self, tags, resource):
        return Tag.objects.add_tags_to_resource(tags, resource)

    def _exists_tag_in_last_resource(self, tag_pk):
        return tag_pk in self._get_last_resource().tags.all().values_list("pk", flat=True)

    def _get_last_resource(self):
        return Resource.objects.last()

    def _add_permissions_for_library_to_user(self):
        permission_add = Permission.objects.get(codename='add_resource')
        permission_delete = Permission.objects.get(codename='delete_resource')
        permission_change = Permission.objects.get(codename='change_resource')
        self.user.user_permissions.add(permission_add)
        self.user.user_permissions.add(permission_delete)
        self.user.user_permissions.add(permission_change)
