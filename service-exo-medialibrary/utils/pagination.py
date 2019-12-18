from rest_framework.pagination import PageNumberPagination

PAGE_SIZE = 12


class BasicPageNumberPagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_size_query_param = 'page_size'
