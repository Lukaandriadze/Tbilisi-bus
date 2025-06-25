from rest_framework.pagination import PageNumberPagination

class ProductPaginaton(PageNumberPagination):
    page_size = 40
    page_size_qery_param = 'page_size'
    max_page_size = 100