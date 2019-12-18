from django.db import models

from invitation.conf import settings as InvitationSettings
from model_utils.models import TimeStampedModel


class NotificationStep(TimeStampedModel):
    email_ok = models.TextField(blank=True, null=True)
    email_ok_subject = models.TextField(blank=True, null=True)
    email_ok_body = models.TextField(blank=True, null=True)

    email_ko = models.TextField(blank=True, null=True)
    email_ko_subject = models.TextField(blank=True, null=True)
    email_ko_body = models.TextField(blank=True, null=True)


class ProcessTemplateStep(TimeStampedModel):
    template = models.ForeignKey(
        'RegistrationProcessTemplate',
        related_name='steps',
        on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    action = models.CharField(
        max_length=20,
        choices=InvitationSettings.INVITATION_CH_TYPE)
    next_steps = models.ManyToManyField(
        'self', symmetrical=False,
        related_name='_previous_steps')
    previous_steps = models.ManyToManyField(
        'self', symmetrical=False,
        related_name='_next_steps')
    email_tpl = models.OneToOneField(
        'NotificationStep',
        on_delete=models.CASCADE)
    options = models.ManyToManyField('ProcessTemplateStepOption')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return '{} {}'.format(self.name, self.code)

    @property
    def is_validation(self):
        raise NotImplementedError


class RegistrationProcessTemplate(TimeStampedModel):

    name = models.CharField(
        max_length=100)
    version = models.IntegerField()

    class Meta:
        ordering = ['-version']

    def __str__(self):
        return '{} [v.{}]'.format(self.name, self.version)

    @property
    def last_step(self):
        return self.steps.all().last()

    @property
    def first_step(self):
        return self.steps.all().first()

    def get_step_by_code(self, code):
        return self.steps.filter(code=code).first()
