from django.contrib.auth import get_user_model

from populate.populator.builder import Builder


User = get_user_model()


class UserBuilder(Builder):

    def create_object(self):
        pass
