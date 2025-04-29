from django.shortcuts import render, redirect
from django.views import View
from .service import CategoryService
from product.service import ProductService

class CategoryPageView(View):
    def get(self, request):
        try:
            # Lấy danh sách category
            categories = CategoryService.list_categories()
            
            # Lấy các tham số lọc và phân trang từ query parameters
            page = request.GET.get('page', 1)
            page_size = request.GET.get('page_size', 5)  # Bạn có thể thay đổi page_size nếu cần
            category_name = request.GET.get('category_name', None)
            min_price = request.GET.get('min_price', None)
            max_price = request.GET.get('max_price', None)

            # Lọc và phân trang sản phẩm
            products_data = ProductService.list_product(
                page=page,
                page_size=page_size,
                category_name=category_name,
                min_price=min_price,
                max_price=max_price
            )
            
            # Truyền các thông tin vào template
            return render(request, 'category_list.html', {
                'categories': categories,
                'page_obj': products_data,
            })
        except Exception as e:
            return render(request, 'category_list.html', {
                'error': str(e),
            })