from .exceptions import MetricException
from .metric import create_metric


class CustomAction:

    verb = None
    user_uuid = None

    def __init__(self, verb, user_uuid):
        self.verb = verb
        self.user_uuid = user_uuid


class ModelMetricMixin:

    METRIC_CATEGORY = None
    METRIC_ACTION_LIST = None

    def _create_custom_action(self, action_verb, user_uuid):
        return CustomAction(verb=action_verb, user_uuid=user_uuid)

    def metric_is_active(self, *args, **kwargs):
        metric_active = False
        if self.METRIC_ACTION_LIST:
            try:
                action = kwargs.get('action')
                assert action
                tracked_metrics_action = dict(self.METRIC_ACTION_LIST).keys()
            except AssertionError:
                raise MetricException(
                    'Missed action param for model {}'.format(
                        self.__class__.__name__,
                    )
                )
            metric_active = action.verb in tracked_metrics_action

        return metric_active

    def get_category(self):
        try:
            assert self.METRIC_CATEGORY
        except AssertionError:
            raise MetricException(
                'Define METRIC_CATEGORY variable for {} objects'.format(
                    self._meta.model.__name__
                ))

        return self.METRIC_CATEGORY

    def get_action(self, action):
        return dict(self.METRIC_ACTION_LIST).get(action.verb)

    def get_label(self, action):
        return 'pk:{}'.format(self.pk)

    def get_value(self):
        return None

    def get_user(self, action):
        return action.actor.uuid

    def create_new_metric(self, action=None):
        if self.metric_is_active(action=action):
            create_metric(
                user='{}'.format(self.get_user(action)),
                category=self.get_category(),
                action=self.get_action(action),
                label=self.get_label(action),
                value=self.get_value(),
            )
