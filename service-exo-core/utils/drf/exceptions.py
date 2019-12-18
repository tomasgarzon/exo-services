from rest_framework.exceptions import APIException
from rest_framework import status


class ObjectDuplicated(APIException):

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail, status_code):
        detail = detail or self.default_detail
        super(ObjectDuplicated, self).__init__(detail)

        if status_code:
            self.status_code = status_code
