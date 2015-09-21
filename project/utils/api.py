from __future__ import absolute_import

from rest_framework.pagination import PageNumberPagination


class DisabledPagination(PageNumberPagination):
    page_size = None
