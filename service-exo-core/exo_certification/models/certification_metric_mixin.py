from utils.metric import ModelMetricMixin

from ..conf import settings


class CertificationRequestMetricMixin(ModelMetricMixin):

    METRIC_CATEGORY = 'Funnel'
    METRIC_ACTION_LIST = settings.EXO_CERTIFICATION_METRIC_ACTION_LIST

    def get_action(self, action):
        return dict(settings.EXO_CERTIFICATION_METRIC_ACTION_LIST).get(action.verb)

    def get_label(self, action):
        label_prefix = dict(settings.EXO_CERTIFICATION_METRIC_LABEL_PREFIX).get(action.verb)
        return label_prefix.format(
            settings.EXO_CERTIFICATION_METRIC_LABELS.get(self.cohort.level)
        )

    def get_value(self):
        return self.price

    def get_user(self, action):
        return action.user_uuid

    def report_pay_action(self):
        custom_action = self._create_custom_action(
            action_verb=settings.EXO_CERTIFICATION_METRIC_ACTION_PAY,
            user_uuid=self.user.uuid,
        )
        self.create_new_metric(custom_action)

    def report_acquire_action(self):
        custom_action = self._create_custom_action(
            action_verb=settings.EXO_CERTIFICATION_METRIC_ACTION_ACQUIRE,
            user_uuid=self.user.uuid,
        )
        self.create_new_metric(custom_action)
