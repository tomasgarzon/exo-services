import json


class PasswordTestMixin:

    def get_token_from_email(self, email_body):
        token = json.loads(email_body.replace("'", '"')).get('public_url').split('/')[3]
        return token
