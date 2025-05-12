# Note: adding custom limit requires to create custom pagination
# Note: test the limit and default to leveraging settings.py
# Note: to be tested on sun

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size_query_param = "limit" 
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            "total": self.page.paginator.count,
            "page": self.page.number,
            "limit": self.get_page_size(self.request),
            "results": data,
        })