from rest_framework.pagination import PageNumberPagination as OriginalPageNumberPagination


class PageNumberPagination(OriginalPageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
