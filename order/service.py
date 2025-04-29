from django.db import transaction
from decimal import Decimal
from .models import Order, OrderDetail
from product.models import Product
from rest_framework.exceptions import PermissionDenied

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(user, phone, address, items):
        if not getattr(user, 'is_authenticated', False):
            raise PermissionDenied("Authentication credentials were not provided.")

        order = Order.objects.create(
            user=user,
            phone=phone,
            address=address
        )
        total = Decimal('0.00')
        details = []
        for item in items:
            product = Product.objects.select_for_update().get(id=item['product_id'])
            quantity = item['quantity']
            price = product.price * quantity
            details.append(
                OrderDetail(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )
            )
            total += price
        OrderDetail.objects.bulk_create(details)
        order.total_price = total
        order.save(update_fields=['total_price'])
        return order

    @staticmethod
    def list_orders(user=None):
        qs = Order.objects.all()
        if getattr(user, 'is_authenticated', False):
            qs = qs.filter(user=user)
        return qs.order_by('-create_at')

    @staticmethod
    def get_order(order_id, user=None):
        qs = Order.objects.prefetch_related('details', 'details__product')
        if getattr(user, 'is_authenticated', False):
            qs = qs.filter(user=user)
        return qs.get(id=order_id)