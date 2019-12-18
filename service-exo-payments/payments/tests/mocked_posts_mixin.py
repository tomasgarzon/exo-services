from rest_framework import status


def mocked_requests(*args, **kwargs):

    class MockResponse:
        def __init__(self, status_code=status.HTTP_200_OK, *args, **kwargs):
            self.status_code = status_code
            self.ok = True

    return MockResponse(**kwargs)
