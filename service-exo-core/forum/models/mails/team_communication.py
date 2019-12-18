from django.conf import settings

from .mixins import PostMailMixin


class TeamCommunicationCreated(PostMailMixin):

    def get_data(self):
        data = super().get_data()
        data.update({
            'post_content': self.post.description,
            'created_by_name': self.post.created_by.get_full_name(),
            'created_by_profile_picture': self.post.created_by.profile_picture.get_thumbnail_url(),
            'created_by_role': self.post.created_by.user_title,
            'tags': list(self.post.tags.all().values_list(
                'name', flat=True,
            )),
            'public_url': settings.FRONTEND_PROJECT_STEP_PAGE.format(
                **{
                    'project_id': self.post.project.id,
                    'team_id': self.post.team.pk,
                    'step_id': self.post.content_object.step.pk,
                    'section': 'learn'}),
        })
        return data


class TeamCommunicationReplied(PostMailMixin):

    def __init__(self, post, answer):
        super().__init__(post)
        self.answer = answer

    def get_data(self):
        data = super().get_data()
        data.update({
            'post_content': self.post.description,
            'answer_content': self.answer.comment,
            'created_by_name': self.answer.created_by.get_full_name(),
            'created_by_profile_picture': self.answer.created_by.profile_picture.get_thumbnail_url(),
            'created_by_role': self.answer.created_by.user_title,
            'public_url': settings.FRONTEND_PROJECT_STEP_PAGE.format(
                **{
                    'project_id': self.post.project.id,
                    'team_id': self.post.team.pk,
                    'step_id': self.post.content_object.step.pk,
                    'section': 'learn'}),
        })
        return data
