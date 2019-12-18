from django.test import TestCase

from ..models import User

from utils.faker_factory import faker


class UserImageProfileTest(TestCase):

    def test_create_user(self):
        user_email = faker.email()
        user_pwd = '123456789'
        user = User.objects.create_user(email=user_email,
                                        password=user_pwd,
                                        short_name=faker.first_name())
        self.assertIsNotNone(user.profile_picture)
        self.assertTrue(user.profile_picture != '')

        for size in user._meta.get_field('profile_picture').thumbnails:
            self.assertIsNotNone(user.profile_picture.get_thumbnail_url(size[0],
                                                                        size[1]))
