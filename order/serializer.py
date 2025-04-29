from rest_framework import serializers
from .models import Order, OrderDetail
from product.models import Product

class OrderDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderDetail
        fields = ('product', 'product_name', 'quantity', 'price')

class OrderSerializer(serializers.ModelSerializer):
    details = OrderDetailSerializer(many=True)
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'phone', 'address', 'total_price', 'create_at', 'details')

class CreateOrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

class CreateOrderSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=10)
    address = serializers.CharField(max_length=100)
    items = CreateOrderItemSerializer(many=True)