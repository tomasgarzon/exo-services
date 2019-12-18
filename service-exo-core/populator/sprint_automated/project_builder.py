import pytz

from datetime import timedelta, datetime

from django.conf import settings
from django.contrib.auth import get_user_model

from populate.populator.builder import Builder
from populate.populator.common.helpers import find_tuple_values

from exo_role.models import ExORole
from relation.models.project import ConsultantProjectRole

from .step_helper import TYPEFORM_URL


class ProjectBuilder(Builder):

    def create_object(self):
        project = self.create_project()
        self.update_zoom_settings(project)
        self.update_project_launch_settings(project)
        self.update_steps(project)
        self.update_roles(project)
        self.update_observers(project)
        self.update_staff(project)
        self.update_delivery_managers(project)
        self.launch_project(project)
        return project

    def update_zoom_settings(self, project):
        zoom_api_key = self.data.get('zoom_api_key')
        zoom_secret_key = self.data.get('zoom_secret_key')
        if zoom_api_key and zoom_secret_key:
            project_ptr = project.project_ptr
            project_ptr.zoom_settings.zoom_api_key = zoom_api_key
            project_ptr.zoom_settings.zoom_secret_key = zoom_secret_key
            project_ptr.zoom_settings.save(
                update_fields=['zoom_api_key', 'zoom_secret_key'])

    def get_template_assignments(self, project):
        template_assignments = self.data.get('template_assignments')
        if template_assignments:
            value = find_tuple_values(
                settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS,
                template_assignments)[0]
            # For now, we have just one template -> Automated Sprint
            if value is not None:
                project.update_assignments_template(value)
            if value == settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS_SPRINT_BOOK:
                self.fix_weekly_quiz(project)
            return value

    def get_lapse(self):
        return find_tuple_values(
            settings.PROJECT_CH_LAPSE,
            self.data.get('lapse'))[0]

    def update_project_launch_settings(self, project):
        launch_settings = project.settings
        launch_settings.launch['send_welcome_consultant'] = \
            self.data.get('send_welcome_consultant', False)
        launch_settings.launch['send_welcome_participant'] = \
            self.data.get('send_welcome_participant', False)
        launch_settings.launch['fix_password'] = self.data.get('password', '')
        self.update_project_settings(project, launch_settings)

    def update_project_settings(self, project, launch_settings):
        launch_settings.participant_step_feedback_enabled = self.data.get('feedback', False)
        launch_settings.participant_step_microlearning_enabled = \
            self.data.get('microlearing', False)
        launch_settings.team_communication = \
            self.data.get('team_comunication', True)
        launch_settings.ask_to_ecosystem = self.data.get('ask_to_ecosystem', True)
        launch_settings.directory = self.data.get('directory', True)
        launch_settings.version = str(self.data.get('version', 2))
        launch_settings.template_assignments = self.get_template_assignments(project)
        launch_settings.save()

    def create_project(self):
        pass

    def launch_project(self, project):
        launched_by = self.data.get('launched_by')
        if launched_by:
            project.launch(launched_by)
            self.update_badges(project)

    def update_badges(self, project):
        time_zone = pytz.utc
        dt = time_zone.localize(datetime.now())
        if project.lapse == settings.PROJECT_LAPSE_WEEK:
            if project.start + timedelta(weeks=project.duration) < dt:
                self.finish_project(project)
        elif project.lapse == settings.PROJECT_LAPSE_DAY:
            if project.start + timedelta(days=project.duration) < dt:
                self.finish_project(project)
        elif project.lapse == settings.PROJECT_LAPSE_PERIOD:
            last_step = project.steps.last()
            if last_step and last_step.end and last_step.end < dt:
                self.finish_project(project)

    def finish_project(self, project):
        user = get_user_model().objects.admin_users().first()
        project.set_finished(user, project.steps.last().end)

    def update_steps(self, project):
        for stp in self.data.get('steps', []):
            step = project.steps.all()[stp.get('day') - 1]
            edge_stream = step.streams.get(
                stream=settings.PROJECT_STREAM_CH_STARTUP)
            edge_stream.goal = stp.get('edge_goal')
            edge_stream.guidelines = stp.get('edge_guidelines', '')
            edge_stream.save(
                update_fields=['goal', 'guidelines'])
            core_stream = step.streams.get(
                stream=settings.PROJECT_STREAM_CH_STRATEGY)
            core_stream.goal = stp.get('core_goal')
            core_stream.guidelines = stp.get('core_guidelines', '')
            core_stream.save(update_fields=['goal', 'guidelines'])

    def update_observers(self, project):
        for obs in self.data.get('observers', []):
            project.add_user_project_supervisor(
                user_from=self.data.get('created_by'),
                name=obs.get('name'),
                email=obs.get('email'))
            self._special_role_user_updated_profile(obs, project)

    def update_staff(self, project):
        for member in self.data.get('staff', []):
            project.add_user_project_staff(
                user_from=self.data.get('created_by'),
                name=member.get('name'),
                email=member.get('email'))
            self._special_role_user_updated_profile(member, project)

    def update_delivery_managers(self, project):
        for admin in self.data.get('delivery_managers', []):
            project.add_user_project_delivery_manager(
                user_from=self.data.get('created_by'),
                name=admin.get('name'),
                email=admin.get('email'))
            self._special_role_user_updated_profile(admin, project)

    def _special_role_user_updated_profile(self, member, project):
        user = get_user_model().objects.filter(
            email=member.get('email')).first()
        user.full_name = member.get('name')
        user.location = project.project_ptr.location
        user.place_id = project.project_ptr.place_id
        user.save()

    def update_roles(self, project):
        for role_data in self.data.get('roles', []):
            consultant = role_data.get('consultant')
            exo_role = ExORole.objects.get(code=role_data.get('code'))
            exo_role_other_name = role_data.get('exo_role_other_name', None)

            ConsultantProjectRole.objects.get_or_create_consultant(
                project.created_by,
                consultant,
                project,
                exo_role,
                exo_role_other_name,
            )

    def fix_weekly_quiz(self, project):
        for step in project.steps.all():
            if step.index in TYPEFORM_URL:
                core_url, edge_url = TYPEFORM_URL.get(step.index)
                self.update_microlearning_url(
                    step=step,
                    stream=settings.PROJECT_STREAM_CH_STRATEGY,
                    url=core_url)
                self.update_microlearning_url(
                    step=step,
                    stream=settings.PROJECT_STREAM_CH_STARTUP,
                    url=edge_url)

    def update_microlearning_url(self, step, stream, url):
        step_stream = step.streams.get(stream=stream)
        microlearning = step_stream.microlearning
        microlearning.typeform_url = url
        microlearning.save(update_fields=['typeform_url'])
