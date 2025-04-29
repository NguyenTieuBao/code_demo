from django.db import models
from account.models import User
from product.models import Product

# Create your models here.
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10, null=False)
    address = models.CharField(max_length=100, null=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    create_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order'
        
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    
class OrderDetail(models.Model):
    order = models.ForeignKey(Order, related_name='details', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    
    class Meta:
        db_table = 'order_detail'
        
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"