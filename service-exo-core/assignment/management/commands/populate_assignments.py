import logging

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

from project.models import Project, Step
from typeform.helpers import PopulatorTypeformMixin
from utils.populator import CommandYAMLMixin

from ...models import (
    AssignmentStep,
    AssignmentTask,
    AssignmentTaskItem,
    InformationBlock,
    AssignmentText,
    AssignmentAdvice,
    AssignmentAdviceItem,
    AssignmentResource,
    AssignmentResourceItem)

logger = logging.getLogger('files')


class Command(PopulatorTypeformMixin, CommandYAMLMixin, BaseCommand):

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

    def handle(self, *args, **kwargs):
        project_pk = kwargs.get('project')[0]
        template_assignments = kwargs.get('template_assignments')[0]
        delete_old_assignments = kwargs.get('delete')[0]
        project = Project.objects.get(pk=project_pk)
        steps = Step.objects.filter_by_project(project).order_by('index')
        exo_data_path = ''

        self.stdout.write(
            self.style.WARNING('Creating assignments ...')
        )

        if delete_old_assignments:
            AssignmentStep.objects.filter_by_project(project).delete()

        head_coach_consultans = project.consultants_roles.filter_by_exo_role_code(
            settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH)

        if head_coach_consultans:
            created_by = head_coach_consultans.first().consultant.user
        else:
            created_by = get_user_model().objects.filter(is_superuser=True).first()

        if template_assignments == settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS_SPRINT_BOOK:
            exo_data_path = '{}/{}'.format(
                settings.BASE_DIR,
                settings.ASSIGNMENT_EXO_DATA_SPRINT_BOOK_PATH,
            )
        elif template_assignments == settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS_LEVEL_1_EN:
            exo_data_path = '{}/{}'.format(
                settings.BASE_DIR,
                settings.ASSIGNMENT_EXO_DATA_CERTIFICATION_LEVEL_1_EN_PATH,
            )
        elif template_assignments == settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS_LEVEL_1_ES:
            exo_data_path = '{}/{}'.format(
                settings.BASE_DIR,
                settings.ASSIGNMENT_EXO_DATA_CERTIFICATION_LEVEL_1_ES_PATH,
            )
        else:
            exo_data_path = template_assignments

        for step in steps:
            files = [
                '{}/assignment_step_{}_edge.yml'.format(exo_data_path, step.index),
                '{}/assignment_step_{}_core.yml'.format(exo_data_path, step.index),
                '{}/assignment_step_{}.yml'.format(exo_data_path, step.index),
            ]

            loaded = False

            for filepath in files:

                try:
                    content = self.load_file(filepath)

                    if filepath.endswith('edge.yml'):
                        streams = [
                            settings.PROJECT_STREAM_CH_STARTUP,  # Edge
                        ]
                    elif filepath.endswith('core.yml'):
                        streams = [
                            settings.PROJECT_STREAM_CH_STRATEGY,  # Core
                        ]
                    else:
                        streams = [
                            settings.PROJECT_STREAM_CH_STARTUP,  # Edge
                            settings.PROJECT_STREAM_CH_STRATEGY,  # Core
                        ]

                    assignment_step = AssignmentStep.objects.create(
                        step=step,
                        name=content.get('name'),
                        settings=content.get('settings', {}),
                        streams=streams,
                        created_by=created_by)

                    self.create_information_blocks(
                        content_object=assignment_step,
                        blocks=content.get('blocks'),
                        created_by=created_by)

                    self.create_typeforms(
                        linked_object=step,
                        typeforms_list=content.get('typeforms', []),
                    )

                    loaded = True

                    self.logger.info(
                        'Assignment: Step [{}] and Teams {} populated'.format(step.name, streams)
                    )

                except FileNotFoundError:  # noqa
                    pass

            if not loaded:
                self.logger.warning(
                    'Assignment: Step {} not populated for project {}'.format(step.name, project.name)
                )

        self.stdout.write(self.style.SUCCESS('Assignments created'))
