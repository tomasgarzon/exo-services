from django.contrib.auth import get_user_model

from rest_framework import authentication


class ZoomAuthentication(authentication.BasicAuthentication):
    def authenticate_credentials(self, userid, password):
        User = get_user_model()
        user = User(email=userid)
        return (user, None)
