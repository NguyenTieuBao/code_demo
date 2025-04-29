from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .service import OrderService
from .serializer import OrderSerializer, CreateOrderSerializer
from .models import Order

class OrderController(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is not None:
            return self.retrieve(request, pk)
        return self.list(request)

    def post(self, request, pk=None):
        return self.create(request)

    def list(self, request):
        orders = OrderService.list_orders(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            order = OrderService.get_order(pk, user=request.user)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def create(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        order = OrderService.create_order(
            user=request.user,
            phone=data['phone'],
            address=data['address'],
            items=data['items']
        )
        out_serializer = OrderSerializer(order)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

