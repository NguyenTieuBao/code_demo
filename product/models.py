from django.db import models
from django.core.validators import MinValueValidator
from category.models import Category
from django.utils.text import slugify

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    size = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(validators=[MinValueValidator(1)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Nếu slug chưa có thì tự tạo từ title
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'product'
        
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='list_image', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product/details')
    
    
    def __str__(self):
        return self.product.title
    
    class Meta:
        db_table = 'product_image'