# python imports
import logging

# django imports
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from model_utils.models import TimeStampedModel

from utils.loader import load_class

# app imports
from .conf import settings
from .helpers import cast_value

logger = logging.getLogger(__name__)


class ConfigParam(TimeStampedModel):
    """A description of a single account configuration parameter.

    E.g. a ConfigParam could be a parameter for config how many
    messages a user can get in a week or if the user can receive an email
    """

    name = models.CharField(
        max_length=80,
        blank=False,
        null=False,
        verbose_name=_('parameter name'),
    )
    param_type = models.CharField(
        max_length=80,
        choices=settings.ACCOUNT_CONF_ALLOWED_TYPES,
        blank=False,
        null=False,
        verbose_name=_('parameter type'),
    )
    _default_value = models.CharField(
        max_length=80,
        blank=False,
        null=False,
        verbose_name=_('default value'),
    )
    group = models.CharField(
        max_length=80,
        choices=settings.ACCOUNT_CONF_CONFIG_GROUPS,
        blank=False,
        null=False,
        verbose_name=_('configuration group'),
    )

    user = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ConfigValue',
        related_name='config_params',
        verbose_name=_('user'),
    )

    condition_for_available = models.CharField(
        blank=True, null=True,
        max_length=200)

    class Meta:
        unique_together = ('name', 'group')

    def __unicode__(self):
        return 'Config {}: {}'.format(self.group, self.name)

    def __str__(self):
        return self.name

    def allowed_agent(self, agent):
        """Indicates if the given agent can use this parameter.

        Which agents can set/get which parameters are setted in the project's
        config file. This method indicates if a agents can use a given param
        based on the agents type.

        Args:
            agent: an agent object of any kind. (User or Consultant)

        Returns:
            A boolean that indicates if the agent can use this parameter.
        """
        model_str = '{}.{}'.format(agent._meta.app_label,
                                   agent._meta.object_name)
        groups = settings.ACCOUNT_CONF_GROUPS
        all_group = groups.get('*', {}).get(self.group, [])
        user_group = groups.get(model_str, {}).get(self.group, [])
        cond_allowed_agend = self.name in set(all_group + user_group)
        cond_allowed_method = True
        if self.condition_for_available:
            condition_class = load_class(self.condition_for_available)()
            cond_allowed_method = condition_class(agent)

        return cond_allowed_agend and cond_allowed_method

    def get_value_for_agent(self, agent):
        """Returns the value for the given agent for this param.

        A agent can have a value setted for all of her ConfigParams. But if
        she has not setted the param this method will return the default
        value.

        Args:
            agent: a agent object of any kind.

        Returns:
            A value of the type setted on the ConfigParam param_type.
        """
        if not self.allowed_agent(agent):
            raise ValueError(
                'Agent {} has no config param {}.{}'.format(
                    agent,
                    self.group,
                    self.name))

        user = agent
        if not isinstance(agent, get_user_model()):
            user = agent.user
        try:
            value_instance = self.values.get(user=user)
        except self.values.model.DoesNotExist:
            value = self._default_value
        else:
            value = value_instance._value

        return cast_value(self.param_type, value)

    @transaction.atomic
    def set_value_for_agent(self, agent, value):
        """Set the value for this param for a given agent.

        This method check if the agent has this param and if the value type
        is correct for the param_type. If everythin is right, it will set
        the value.

        Args:
            agent: a agent object of any kind.
            value: a value of any kind that will be setted for this param.

        Raises:
            TypeError; if given a value of a different type than the param
            type.
        """

        if not self.allowed_agent(agent):
            raise ValueError(
                'Agent {} has no config param {}.{}'.format(
                    agent, self.group, self.name))
        if type(value).__name__ != self.param_type:
            raise TypeError(
                'Param expects {} type. Type {} recieved'.format(
                    self.param_type,
                    type(value).__name__))

        user = agent
        if not isinstance(agent, get_user_model()):
            user = agent.user
        value_instance = self.values.update_or_create(
            user=user,
            config_parameter=self,
            defaults={'_value': str(value)})
        return value_instance


class ConfigValue(models.Model):
    """An instance of a ConfigParam, a defined value for a given user.

    ConfigParam defines the param itself, ConfigValue is a value for that
    param for a given user. For instance, if the ConfigParam defines how
    many message an user can get in a week, the ConfigValue can be 0, 1, 2,
    etc.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        null=False,
        related_name='config_values',
        verbose_name=_('user'),
        on_delete=models.CASCADE,
    )
    config_parameter = models.ForeignKey(
        'ConfigParam',
        blank=False,
        null=False,
        related_name='values',
        verbose_name=_('config parameter'),
        on_delete=models.CASCADE,
    )

    _value = models.CharField(
        max_length=80,
        verbose_name=_('value'),
    )

    class Meta:
        verbose_name = _('Config value')
        verbose_name_plural = _('Config values')
        unique_together = ('user', 'config_parameter', )

    def __unicode__(self):
        return '{} - {}: {}'.format(
            self.config_parameter,
            self.user,
            self._value)

    def __str__(self):
        return self.config_parameter.name
