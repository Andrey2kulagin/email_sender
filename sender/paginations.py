from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_page_size(self, request):
        if 'all_objects' in request.query_params:
            return None  # Возвращает все объекты, если параметр all_objects указан
        return super().get_page_size(request)
