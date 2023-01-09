from rest_framework.pagination import PageNumberPagination


class DisabledPagination(PageNumberPagination):
    page_size = None
