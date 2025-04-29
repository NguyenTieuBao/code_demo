from django.urls import path
from .controller import ProductList, ProductCreate, ProductUpdate, ProductBySlug, ProductDelete
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", ProductList.as_view(), name="list-products"),
    path("<str:slug>", ProductBySlug.as_view(), name="get-product-by-slug"),
    path("create/", ProductCreate.as_view(), name="create-products"),
    path("update/<int:pk>", ProductUpdate.as_view(), name="update-products"),
    path("delete/<int:pk>", ProductDelete.as_view(), name="delete-product")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)