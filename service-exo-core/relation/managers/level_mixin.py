from django.conf import settings


class LevelMixin():
    MAX_LEVEL_KEYWORD = 3

    def highest_level(self):
        return self.get_queryset().filter(level=self.MAX_LEVEL_KEYWORD)

    def at_least_minium_level(self):
        return self.get_queryset().filter(level__gte=settings.RELATION_MIN_KEYWORD_LEVEL)
