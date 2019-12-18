from .mixins import PostMailMixin


class PostCircleCreated(PostMailMixin):

    def get_data(self):
        data = super().get_data()
        data.update({
            'created_by_name': self.post.created_by.get_full_name(),
            'created_by_profile_picture': self.post.created_by.profile_picture.get_thumbnail_url(),
            'created_by_role': self.post.created_by.user_title,
            'circle_name': self.post.content_object.name,
            'post_content': self.post.description,
            'subject_args': {
                'created_by_name': self.post.created_by.get_full_name(),
                'circle_name': self.post.content_object.name,
            },
        })
        return data


class PostAnnouncementCreated(PostMailMixin):

    def get_data(self):
        data = super().get_data()
        data.update({
            'post_content': self.post.description,
            'created_by_name': self.post.created_by.get_full_name(),
            'created_by_profile_picture': self.post.created_by.profile_picture.get_thumbnail_url(),
            'created_by_role': self.post.created_by.user_title,
        })
        return data


class PostAnnouncementReplied(PostMailMixin):

    def __init__(self, post, answer):
        super().__init__(post)
        self.answer = answer

    def get_data(self):
        data = super().get_data()
        data.update({
            'answer_content': self.answer.comment,
            'created_by_name': self.answer.created_by.get_full_name(),
            'created_by_profile_picture': self.answer.created_by.profile_picture.get_thumbnail_url(),
            'created_by_role': self.answer.created_by.user_title,
        })
        return data
