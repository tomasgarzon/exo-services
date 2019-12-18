from rest_framework.pagination import PageNumberPagination


class BasicPageNumberPagination(
        PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'


class ForumCommonMixin:
    def get_liked(self, obj):
        user = self.context['request'].user
        return obj.have_liked(user)

    def get_num_likes(self, obj):
        return obj.counter_up_votes

    def get_seen(self, obj):
        user = self.context['request'].user
        return obj.has_seen(user)

    def get_your_rating(self, obj):
        try:
            return obj.ratings_user.get(self.context['request'].user.pk)
        except AttributeError:
            return None

    def get_counter_rating(self, obj):
        try:
            return obj.counter_rating
        except AttributeError:
            return 0

    def get_avg_rating(self, obj):
        try:
            return obj.average_rating
        except AttributeError:
            return 0
