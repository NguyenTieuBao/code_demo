from .models import Category
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

class CategoryService:
    @staticmethod
    def list_categories():
        return Category.objects.all()
    
    
    @staticmethod
    def get_by_id_category(pk):
        return get_object_or_404(Category, pk=pk)
    
    
    @staticmethod
    def create_category(data):
        return Category.objects.create(**data)
    
    @staticmethod 
    def update_category(pk, data):
        cat = get_object_or_404(Category, pk=pk)
        for attr, value in data.items():
            setattr(cat, attr, value)
        cat.save()
        return cat
    
    @staticmethod
    def delete_category(pk):
        cat = get_object_or_404(Category, pk=pk)
        if cat.products.exists():
            raise ValidationError('Không được xóa danh mục này vì còn sản phẩm của nó.')
        cat.delete()