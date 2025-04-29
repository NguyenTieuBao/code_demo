from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated 
from .serializer import RegisterSerializer, LoginSerializer, ChangePasswordSerializer, PasswordResetSerializer, PasswordResetRequestSerializer
from .service import AccountService
from .models import User
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = AccountService.register(
            username=serializer.validated_data['username'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            phone=serializer.validated_data['phone'],
            role=serializer.validated_data['role']
        )
        return Response({'message': 'Đăng ký thành công.'}, status=status.HTTP_201_CREATED)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = AccountService.login(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if not tokens:
            return Response({'message': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(tokens, status=status.HTTP_200_OK)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'message': 'Refresh token required.'}, status=status.HTTP_400_BAD_REQUEST)
        AccountService.logout(refresh_token)
        return Response({'message': 'Đăng xuất thành công'}, status=status.HTTP_204_NO_CONTENT)
    
    
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            message = AccountService.change_user_password(
                request.user,
                serializer.validated_data['old_password'],
                serializer.validated_data['new_password']
            )
            return Response({"message": message}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class PasswordResetRequestAPIView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data['email'])
        token_obj = AccountService.create_token(user)
        reset_url = AccountService.build_reset_url(request, token_obj)
        AccountService.send_reset_email(user, reset_url)

        return Response({ 'detail': 'Đã gửi email reset password. Vui lòng kiểm tra hộp thư.' }, status=status.HTTP_200_OK)

class PasswordResetConfirmAPIView(APIView):
    def post(self, request, token):
        data = { 'token': token, 'new_password': request.data.get('new_password') }
        serializer = PasswordResetSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({ 'detail': 'Đổi mật khẩu thành công.' }, status=status.HTTP_200_OK)