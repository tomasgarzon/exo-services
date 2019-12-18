class Request:
    _user = None
    query_params = {}

    def __init__(self, user):
        self._user = user

    @property
    def user(self):
        return self._user
