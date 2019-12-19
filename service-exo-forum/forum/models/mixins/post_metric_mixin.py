from utils.metric import ModelMetricMixin

from ...conf import settings


class PostMetricMixin(ModelMetricMixin):

    METRIC_ACTION_LIST = settings.FORUM_METRIC_ACTIONS_LIST

    def get_category(self):
        return settings.FORUM_METRIC_CATEGORIES.get(self._type)
