from .mixins import PostMailMixin


class ForumMentionCreatedMixin(PostMailMixin):

    def get_data(self, mentioned_user):
        data = super().get_data()
        data.update({
            'recipients': [mentioned_user.email],
            'circle_name': self.post.category_name,
        })

        return data


class PostMentionCreated(ForumMentionCreatedMixin):

    def get_data(self, mentioned_user):
        data = super().get_data(mentioned_user)
        data.update({
            'post_content': self.post.description,
            'created_by_name': self.post.created_by.full_name,
            'created_by_role': self.post.created_by.user_title,
            'created_by_profile_picture': self.post.created_by.profile_picture.get_thumbnail_url(),
        })

        return data


class AnswerMentionCreated(ForumMentionCreatedMixin):

    def __init__(self, post, answer):
        super().__init__(post)
        self.answer = answer

    def get_data(self, mentioned_user):
        data = super().get_data(mentioned_user)
        data.update({
            'answer_content': self.answer.comment,
            'created_by_name': self.answer.created_by.full_name,
            'created_by_role': self.answer.created_by.user_title,
            'created_by_profile_picture': self.answer.created_by.profile_picture.get_thumbnail_url(),
        })

        return data
