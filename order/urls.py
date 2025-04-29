# orders/urls.py
from django.urls import path
from .controller import OrderController

urlpatterns = [
    path("orders/", OrderController.as_view(), name="order-list-create"),
    path("orders/<int:pk>/", OrderController.as_view(), name="order-detail"),
]
