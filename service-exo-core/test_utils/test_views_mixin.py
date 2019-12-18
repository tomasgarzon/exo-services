
class TestViewMixin:

    def setUp(self):
        super().setUp()

    def get(self, *args, **kwargs):
        return self.client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.client.post(*args, **kwargs)

    def login(self, *args, **kwargs):
        return self.client.login(*args, **kwargs)

    def _check_url(self, url, username=None, password=None):
        if username and password:
            self.client.logout()
            logged = self.login(username=username, password=password)
            self.assertTrue(logged)

        return self.get(url)
