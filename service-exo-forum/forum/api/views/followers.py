from ..views.mixins import FollowerListMixin, BasicPageNumberPagination


class FollowersAPIView(FollowerListMixin):
    pagination_class = BasicPageNumberPagination


class MentionsAPIView(FollowerListMixin):

    def get_queryset(self):
        return super().get_queryset()[0:5]
