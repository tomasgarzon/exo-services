import yaml
from collections import OrderedDict

from django.views.generic.detail import DetailView
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from assignment.management.commands.populate_assignments import Command
from assignment.models import AssignmentStep
from project.views.mixin import ProjectPermissionMixin

from ...forms.step import StepImportYml
from ...models import Step


def represent_dictionary_order(self, dict_data):
    return self.represent_mapping('tag:yaml.org,2002:map', dict_data.items())


def setup_yaml():
    yaml.add_representer(OrderedDict, represent_dictionary_order)


class StepDetailView(ProjectPermissionMixin, DetailView):
    model = Step
    template_name = 'project/steps/detail.html'


class StepExportView(ProjectPermissionMixin, DetailView):
    model = Step

    def get(self, request, pk, *args, **kwargs):
        setup_yaml()
        step = self.get_object()
        assignment = step.assignments_step.first()

        data = OrderedDict()
        data['name'] = assignment.name
        data['settings'] = assignment.settings
        data['blocks'] = []

        for k in assignment.blocks.all():
            block = OrderedDict({
                'title': k.title, 'subtitle': k.subtitle, 'order': k.order,
                'type': k.get_type_display()})
            if k.type == settings.ASSIGNMENT_INFORMATION_BLOCK_CH_TYPE_TEXT:
                block['text'] = k.assignments_text.text
            elif k.type == settings.ASSIGNMENT_INFORMATION_BLOCK_CH_TYPE_ADVICE:
                block['advices'] = []
                for advice in k.assignment_advices.assignment_advice_items.all():
                    advice_item = OrderedDict({'description': advice.description, 'order': advice.order})
                    block['advices'].append(advice_item)
            elif k.type == settings.ASSIGNMENT_INFORMATION_BLOCK_CH_TYPE_RESOURCE:
                block['resources'] = []
                for resource in k.assignment_resources.assignment_resource_items.all():
                    resource_item = OrderedDict({
                        'name': resource.name,
                        'type': resource.get_type_display(), 'status': resource.get_status_display(),
                        'description': resource.description, 'order': resource.order, 'iframe': resource.iframe,
                        'link': resource.link})
                    block['resources'].append(resource_item)
            data['blocks'].append(block)
        content = yaml.dump(data, default_flow_style=False)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="step_{}.yml"'.format(step.index)
        return response


class StepImportYMLView(ProjectPermissionMixin, DetailView):
    model = Step
    template_name = 'project/steps/import_form.html'
    form_class = StepImportYml

    def get(self, request, pk, *args, **kwargs):
        self.form = self.form_class()
        return super().get(request, pk, *args, **kwargs)

    def post(self, request, pk, *args, **kwargs):
        self.form = self.form_class(request.POST, request.FILES)
        if self.form.is_valid():
            step = self.get_object()
            streams = self.form.cleaned_data.get('streams')
            step.assignments_step.filter(streams=streams).delete()
            stream = self.form.files.get('file').read()
            content = yaml.safe_load(stream)
            assignment_step = AssignmentStep.objects.create(
                step=step,
                name=content.get('name'),
                settings=content.get('settings', {}),
                streams=streams,
                created_by=request.user)
            cc = Command()
            cc.create_information_blocks(
                assignment_step, content.get('blocks'),
                created_by=request.user)
            return HttpResponseRedirect(reverse('project:project:steps', kwargs={'project_id': step.project.pk}))
        return self.get(request, pk, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form'] = self.form
        return context
