import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from data import paths
from utils.populator import CommandYAMLMixin
from assignment.models import (
    AssignmentStep,
    AssignmentTask,
    AssignmentTaskItem,
    InformationBlock,
    AssignmentText,
    AssignmentAdvice,
    AssignmentAdviceItem,
    AssignmentResource,
    AssignmentResourceItem)

from ...models import Project, Step

logger = logging.getLogger('service')


class Command(CommandYAMLMixin, BaseCommand):

    def __init__(self, *args, **kwargs):
        self.logger = logger
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('-p', '--project', nargs='+', type=int)
        parser.add_argument('-t', '--template_assignments', nargs='+', type=str)
        parser.add_argument('-d', '--delete', nargs='+', type=int)

    def create_task_block_and_task_items(self, block, tasks, created_by):
        assignment_task = AssignmentTask.objects.create(block=block)

        for task in tasks:
            assignment_task_item = AssignmentTaskItem.objects.create(
                assignment_task=assignment_task,
                name=task.get('name'),
                order=task.get('order'))

            if task.get('blocks'):
                self.create_information_blocks(
                    content_object=assignment_task_item,
                    blocks=task.get('blocks'),
                    created_by=created_by)

    def create_resource_block_and_resources(self, block, resources, created_by):
        assignment_resource = AssignmentResource.objects.create(block=block)

        for resource in resources:
            AssignmentResourceItem.objects.create(
                assignment_resource=assignment_resource,
                name=resource.get('name'),
                type=self.find_tuple_values(
                    settings.ASSIGNMENT_CH_RESOURCE_ITEM_TYPE,
                    resource.get('type'))[0],
                status=self.find_tuple_values(
                    settings.ASSIGNMENT_CH_RESOURCE_ITEM_STATUS,
                    resource.get('status'))[0],
                link=resource.get('link'),
                description=resource.get('description'),
                thumbnail=resource.get('thumbnail', None),
                iframe=resource.get('iframe', None),
                order=resource.get('order'),
                created_by=created_by)
        return assignment_resource

    def create_advise_block_and_advices(self, block, advices, created_by):
        assignment_advice = AssignmentAdvice.objects.create(block=block)
        for advice in advices:
            AssignmentAdviceItem.objects.create(
                assignment_advice=assignment_advice,
                description=advice.get('description'),
                order=advice.get('order'),
                created_by=created_by)

    def create_text_block(self, block, text, created_by):
        AssignmentText.objects.create(
            block=block,
            text=text,
            created_by=created_by)

    def create_information_blocks(self, content_object, blocks, created_by):

        if blocks:
            for block_data in blocks:
                block = InformationBlock.objects.create(
                    title=block_data.get('title'),
                    subtitle=block_data.get('subtitle'),
                    order=block_data.get('order'),
                    type=self.find_tuple_values(
                        settings.ASSIGNMENT_INFORMATION_BLOCK_CH_TYPES,
                        block_data.get('type'))[0],
                    content_object=content_object,
                    created_by=created_by,
                    section=block_data.get(
                        'section',
                        settings.ASSIGNMENT_INFORMATION_BLOCK_CH_SECTION_DEFAULT),
                )

                block_type = block.type

                if block_type == settings.ASSIGNMENT_INFORMATION_BLOCK_CH_TYPE_TEXT:
                    self.create_text_block(
                        block=block,
                        text=block_data.get('text'),
                        created_by=created_by)
                elif block_type == settings.ASSIGNMENT_INFORMATION_BLOCK_CH_TYPE_ADVICE:
                    self.create_advise_block_and_advices(
                        block=block,
                        advices=block_data.get('advices'),
                        created_by=created_by)
                elif block_type == settings.ASSIGNMENT_INFORMATION_BLOCK_CH_TYPE_RESOURCE:
                    self.create_resource_block_and_resources(
                        block=block,
                        resources=block_data.get('resources'),
                        created_by=created_by)
                elif block_type == settings.ASSIGNMENT_INFORMATION_BLOCK_CH_TYPE_TASK:
                    self.create_task_block_and_task_items(
                        block=block,
                        tasks=block_data.get('tasks'),
                        created_by=created_by)

    def delete_old_assignments(self, delete):
        if delete:
            AssignmentStep.objects.filter_by_project(self.project).delete()

    def get_streams(self, filepath):
        streams = []
        if filepath.endswith('edge.yml'):
            streams = [
                settings.UTILS_STREAM_CH_EDGE,  # Edge
            ]
        elif filepath.endswith('core.yml'):
            streams = [
                settings.UTILS_STREAM_CH_CORE,  # Core
            ]
        else:
            streams = [
                settings.UTILS_STREAM_CH_EDGE,  # Edge
                settings.UTILS_STREAM_CH_CORE,  # Core
            ]
        return streams

    def create_assignment_step(self, step, content, filepath):
        streams = self.get_streams(filepath)
        assignment_steps = AssignmentStep.objects.create(
            step=step,
            name=content.get('name'),
            settings=content.get('settings', {}),
            created_by=self.project.created_by)
        assignment_steps.streams.add(*self.project.streams.filter(code__in=streams))
        return assignment_steps

    def handle(self, *args, **kwargs):
        self.project = Project.objects.get(pk=kwargs.get('project')[0])
        logger.info('\nAssignments populator - Project: {}'.format(self.project.name))
        self.delete_old_assignments(kwargs.get('delete')[0])
        data_path = paths.PROJECT_ASSIGNMENTS_PATH.format(kwargs.get('template_assignments')[0])

        for step in Step.objects.filter_by_project(self.project).order_by('index'):
            files = [
                '{}/assignment_step_{}_edge.yml'.format(data_path, step.index),
                '{}/assignment_step_{}_core.yml'.format(data_path, step.index),
                '{}/assignment_step_{}.yml'.format(data_path, step.index),
            ]

            loaded = False

            for filepath in files:
                try:
                    content = self.load_file(filepath)

                    assignment_step = self.create_assignment_step(step, content, filepath)

                    self.create_information_blocks(
                        content_object=assignment_step,
                        blocks=content.get('blocks'),
                        created_by=self.project.created_by)

                    loaded = True

                except FileNotFoundError:  # noqa
                    pass

            if not loaded:
                self.logger.warning('Assignment: Step {} not populated'.format(step.name))

        logger.info('Assignments populator finished - Project: {}'.format(self.project.name))
