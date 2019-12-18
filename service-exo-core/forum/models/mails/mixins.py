class PostMailMixin:
    def __init__(self, post):
        self.post = post

    def get_data(self):

        return {
            'post_title': self.post.title,
            'public_url': self.post.url,
        }
