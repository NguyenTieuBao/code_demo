from django.urls import path
from .controller import CategoryList, CategoryById, CategoryCreate, CategoryDelete
from .views import CategoryPageView

urlpatterns = [
    path("", CategoryList.as_view(), name="list-categories"),
    path("<int:pk>/", CategoryById.as_view(), name="get-category-by-id"),
    path("create/", CategoryCreate.as_view(), name="create-category"),
    path("delete/<int:pk>", CategoryDelete.as_view(), name="delete-category"),
    
    path('categories/', CategoryPageView.as_view(), name='category_page'),
]