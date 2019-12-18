from utils.metric import ModelMetricMixin

from ..conf import settings


class CircleMetricMixin(ModelMetricMixin):

    METRIC_CATEGORY = 'Circle'
    METRIC_ACTION_LIST = settings.CIRCLES_METRIC_ACTIONS_LIST
