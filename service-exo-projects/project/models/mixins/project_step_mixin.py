from django.utils import timezone


class ProjectStepMixin:

    def current_step(self, date=None):
        if not date:
            date = timezone.now()
        steps = self.steps.filter(start__lte=date, end__gte=date)
        if steps:
            return steps.first()
        steps = self.steps.filter(start__lte=date).order_by('-start')
        if steps:
            return steps.first()
        steps = self.steps.filter(end__lte=date).order_by('-end')
        if steps:
            return steps.first()

        return self.steps.first()
