from django.views.generic.edit import UpdateView
from django.core.exceptions import ValidationError

from .crud import StepCUMixin
from ...models import StepStream
from ...forms.step import StepStreamFactory, StepPeriodStreamFactory, StepForm


class StepEditView(StepCUMixin, UpdateView):
    form_class = StepStreamFactory

    def get_form_kwargs(self):
        kwargs = {
            'queryset': StepStream.objects.filter_by_step(self.get_object()),
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs


class StepEditPeriodView(StepCUMixin, UpdateView):
    form_class = StepPeriodStreamFactory
    template_name = 'project/steps/form_period.html'

    def get_context_data(self, **kwargs):
        context = super(StepEditPeriodView, self).get_context_data(**kwargs)
        step = self.get_object()
        context['form_step'] = StepForm(instance=step)
        return context

    def get_form_kwargs(self):
        kwargs = {
            'queryset': StepStream.objects.filter_by_step(self.get_object()).order_by('-stream'),
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        step_form = StepForm(request.POST, instance=self.object)

        if step_form.is_valid():
            step_form.save()
            return super().post(request, *args, **kwargs)
        else:
            return ValidationError('invalid')
