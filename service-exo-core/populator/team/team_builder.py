from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from team.faker_factories import FakeTeamFactory
from learning.faker_factories import FakeUserMicroLearningFactory
from opportunities.models import OpportunityTeamGroup

from populate.populator.builder import Builder
from populate.populator.common.helpers import find_tuple_values
from populator import BASE_DIR


class TeamBuilder(Builder):
    images_path = '/exo_account/images/'

    def create_object(self):
        team = self.create_team(
            uuid=self.data.get('uuid'),
            name=self.data.get('name'),
            project=self.data.get('project'),
            stream=self.data.get('stream'),
            coach=self.data.get('coach'),
            created_by=self.data.get('created_by'),
            zoom_id=self.data.get('zoom_id'))

        self.update_members(
            team=team,
            members=self.data.get('members'),
            created_by=self.data.get('created_by'))
        self.create_opportunity_group(team)
        return team

    def create_team(self, uuid, name, project, stream, coach, created_by, zoom_id):
        return FakeTeamFactory(
            project=project.project_ptr,
            uuid=uuid,
            name=name,
            stream=find_tuple_values(
                settings.PROJECT_STREAM_CH_TYPE, stream)[0],
            coach=coach,
            created_by=created_by,
            user_from=created_by,
            zoom_id=zoom_id)

    def update_members(self, team, members, created_by):
        team.update_members(user_from=created_by, members=members)
        for member in members:
            user = get_user_model().objects.get(email=member.get('email'))
            if member.get('updated_profile', False):
                user = get_user_model().objects.get(email=member.get('email'))
                user.location = team.project.location
                user.place_id = team.project.place_id
                user.save()
            microlearnings = member.get('microlearnings')
            if microlearnings:
                self.user_microlearnings(
                    user=user,
                    team=team,
                    microlearnings=microlearnings)
            if member.get('uuid'):
                user.uuid = member.get('uuid')
                user.save()
            if member.get('image'):
                self.update_image(user, member.get('image'))
        return team

    def user_microlearnings(self, user, team, microlearnings):
        for microlearning_data in microlearnings:
            step = team.project.steps.all()[microlearning_data.get('step') - 1]
            step_stream = step.streams.get(stream=team.stream)
            microlearning = step_stream.microlearning

            user_micro_learning = FakeUserMicroLearningFactory(
                microlearning=microlearning,
                user=user)

            # Simulate Typeform webhook
            user_micro_learning.add_typeform_response(
                score=microlearning_data.get('score'),
                response='')

    def update_image(self, user, name):
        file_path = '{}{}'.format(BASE_DIR, self.images_path)
        filename = '{}{}.jpg'.format(file_path, name)
        with open(filename, 'rb') as f:
            content_file = ContentFile(f.read())
        user.profile_picture.save(
            '%s.jpg' % (user.get_letter_initial()),
            content_file,
            save=True,
            default=True,
        )

    def create_opportunity_group(self, team):
        if self.data.get('group_uuid'):
            OpportunityTeamGroup.objects.update_or_create(
                team=team,
                defaults={
                    'group_uuid': self.data.get('group_uuid')})
