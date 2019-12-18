from django.contrib.auth import get_user_model


User = get_user_model()


class ForumUser:
    user = None
    total_answers = 0


class ForumUserManager:

    def get_user_more_upvotes(self, posts, size=5):
        return []

    def get_user_more_answers(self, posts, size=5):
        users = {}
        for post in posts:
            for answer in post.answers.all():
                if answer.created_by.pk not in users:
                    users[answer.created_by.pk] = 0
                users[answer.created_by.pk] += 1
        sorted_user = [(k, users[k]) for k in sorted(users, key=users.get, reverse=True)]
        results = []
        for user_id, answers in sorted_user:
            new_user = User.objects.get(pk=user_id)
            forum_user = ForumUser()
            forum_user.user = new_user
            forum_user.total_answers = answers
            results.append(forum_user)
            if len(results) == size:
                break
        return results


user_manager = ForumUserManager()
