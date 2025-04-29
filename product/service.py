from .models import Product, ProductImage
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from unidecode import unidecode
from django.core.paginator import Paginator, EmptyPage

from django.core.paginator import Paginator, EmptyPage

class ProductService:
    @staticmethod
    def list_product(page=1, page_size=5, category_name=None, min_price=None, max_price=None, title=None):
        products = Product.objects.all()

        # Tìm kiếm theo tên sản phẩm
        if title:
            products = products.filter(title__icontains=title)

        if category_name:
            products = products.filter(category__name=category_name)

        if min_price == '':
            min_price = None
        if max_price == '':
            max_price = None

        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)

        paginator = Paginator(products, page_size)

        try:
            paginated_products = paginator.page(page)
            products_list = paginated_products.object_list
        except EmptyPage:
            products_list = []
            page = 1

        return {
            "products": products_list,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "total_items": paginator.count
        }

    
    @staticmethod
    def get_product_slug(slug):
        return get_object_or_404(Product, slug=slug)
    
    @staticmethod
    def create_product(data):
        return Product.objects.create(**data)
    
    @staticmethod
    def update_product(pk, data):
        pro = get_object_or_404(Product, pk=pk)
        for attr, value in data.items():
            setattr(pro, attr, value)
        if 'name' in data:
            pro.slug = slugify(unidecode(data['name']))
        pro.save()
        return pro
    
    @staticmethod
    def delete_product(pk):
        pro = get_object_or_404(Product, id=pk)
        pro.delete()
        
    @staticmethod
    def get_products_by_name(keyword, page=1, page_size=5):
        # Lấy tất cả sản phẩm có tên chứa từ khóa
        products = Product.objects.filter(name__icontains=keyword)
        
        # Phân trang
        paginator = Paginator(products, page_size)
        try:
            paginated_products = paginator.page(page)
            products_list = paginated_products.object_list
        except EmptyPage:
            products_list = []
            page = 1

        return {
            "products": products_list,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "total_items": paginator.count
        }
      
    @staticmethod  
    def save_product_images(product_id, image_files):
    
        try:
            # Lấy sản phẩm theo ID
            product = Product.objects.get(id=product_id)

            # Lưu từng hình ảnh vào bảng ProductImage
            for image_file in image_files:
                product_image = ProductImage(product=product, image=image_file)
                product_image.save()

            return product

        except Product.DoesNotExist:
            raise ValueError("Sản phẩm không tồn tại.")