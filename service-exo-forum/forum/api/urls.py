from django.conf.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    post, post_slug, post_category,
    feed, answer, followers, categories)

app_name = 'forum'

router = DefaultRouter()
router.register(
    r'post',
    post.PostViewSet,
    base_name='post',
)
router.register(
    r'answer',
    answer.AnswerViewSet,
    base_name='answer',
)
router.register(
    r'categories/(?P<slug>[-\w]+)/posts',
    post_category.PostCategoryViewSet,
    base_name='circle-post'
)
router.register(
    r'post-slug',
    post_slug.PostSlugViewSet,
    base_name='post-slug'
)
router.register(
    r'categories',
    categories.ForumCategoryViewSet,
    base_name='categories'
)

urlpatterns = [
    path(
        r'^',
        include(router.urls),
    ),
    path(
        'feed/',
        feed.PostFeedListView.as_view(),
        name='feed',
    ),
    path(
        '<slug:slug>/followers/$',
        followers.FollowersAPIView.as_view(),
        name='followers'
    ),
    path(
        '<slug:slug>/mentions/$',
        followers.MentionsAPIView.as_view(),
        name='mentions'
    ),
]
