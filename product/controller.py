from rest_framework.response import Response
from rest_framework import status 
from rest_framework.views import APIView
from .serializer import ProductSerializer
from .service import ProductService


class ProductList(APIView):
    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        category_name = request.query_params.get('category')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        
        if min_price is not None:
            min_price = float(min_price)
        if max_price is not None:
            max_price = float(max_price)

        data = ProductService.list_product(
            page=page, 
            page_size=page_size, 
            category_name=category_name,
            min_price=min_price,
            max_price=max_price
        )

        serializer = ProductSerializer(data["products"], many=True)

        return Response({
            "page": data["current_page"],
            "total_pages": data["total_pages"],
            "total_items": data["total_items"],
            "products": serializer.data
        }, status=status.HTTP_200_OK)
        
class ProductBySlug(APIView):
    def get(self, request, slug):
        try:
            pro = ProductService.get_product_slug(slug)
            serializer = ProductSerializer(pro).data
            return Response(serializer)
        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        
        
class ProductCreate(APIView):
    def post(self, request):
        try:
            serializer = ProductSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            pro = ProductService.create_product(serializer.validated_data)
            return Response(ProductSerializer(pro).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ProductUpdate(APIView):
    def put(self, request, pk):
        try:
            pro = ProductService.update_product(pk, request.data)
            serializer = ProductSerializer(pro)
            return Response(serializer.data, status=status.HTTP_200_OK) 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
        
class ProductDelete(APIView):
    def delete(self, request, pk):
        try:
            ProductService.delete_product(pk)
            return Response({"message": "Đã xóa thành công"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    