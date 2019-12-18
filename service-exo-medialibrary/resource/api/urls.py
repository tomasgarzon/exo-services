from django.urls import path

from rest_framework import routers

from .views import (
    resource_library, resource_library_project,
    resource_validate_url,
    tag_list, category_list)

app_name = 'resources'

router = routers.SimpleRouter()

router.register('tag', tag_list.TagViewSet, basename="tag")
router.register('category', category_list.CategoryViewSet, basename="category")
router.register('library', resource_library.ResourceLibraryViewSet, basename="library")
router.register('library-project', resource_library_project.ResourceLibraryProjectViewSet, basename="library-project")


urlpatterns = router.urls


urlpatterns += [
    path('validate-url/', resource_validate_url.ResourceValidateURLView.as_view(), name='validate-url'),
    path('post-save-project/', resource_library_project.ResourcePostSaveProjectView.as_view(), name='post-save-project')
]
