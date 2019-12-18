from .mixins import PostMailMixin


class AskToEcosystemCreated(PostMailMixin):

    def get_data(self):
        data = super().get_data()
        data.update({
            'created_by_name': self.post.created_by.get_full_name(),
            'created_by_profile_picture': self.post.created_by.profile_picture.get_thumbnail_url(),
            'created_by_role': self.post.created_by.user_title,
            'post_content': self.post.description,
        })
        return data


class AskToEcosystemReplied(PostMailMixin):
    def __init__(self, post, answer):
        super().__init__(post)
        self.answer = answer

    def get_data(self):
        data = super().get_data()
        data.update({
            'created_by_name': self.answer.created_by.get_full_name(),
            'created_by_profile_picture': self.answer.created_by.profile_picture.get_thumbnail_url(),
            'created_by_role': self.answer.created_by.user_title,
            'answer_content': self.answer.comment,
        })
        return data
