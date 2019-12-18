from django.views import View
from django.http import JsonResponse

from time import time

from forum.models import Post

from ..redis.redis_cache_mixin import RedisCacheMixin


class PerformanceView(View):

    def test_method(self):
        raise NotImplementedError

    def get(self, request):
        start = time()
        data = self.test_method()
        stop = time()
        duration = stop - start
        data['duration'] = '%.3f' % duration
        return JsonResponse(data)


class PosgreSQLPerformanceView(PerformanceView):

    def test_method(self):
        data = {}
        data['post'] = Post.objects.all().prefetch_related('answers', 'created_by').count()
        return data


class RedisPerformanceView(PerformanceView):

    def test_method(self):
        data = {}
        connection = RedisCacheMixin()
        connection._set_value('foo', 'var')
        data['redis'] = connection._get_value('foo')
        return data
