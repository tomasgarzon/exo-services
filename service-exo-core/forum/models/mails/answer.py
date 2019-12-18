from .mixins import PostMailMixin


class PostAnswerRating(PostMailMixin):

    def __init__(self, post, answer, rating):
        super().__init__(post)
        self.answer = answer
        self.rating = rating

    def get_data(self):
        data = super().get_data()
        data.update({
            'answer_content': self.answer.comment,
            'answer_rating': self.rating,
            'created_by_name': self.answer.created_by.get_full_name(),
            'created_by_profile_picture': self.answer.created_by.profile_picture.get_thumbnail_url(),
            'created_by_role': self.answer.created_by.user_title,
        })
        return data
