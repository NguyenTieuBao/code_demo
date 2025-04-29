from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import timedelta
from .models import PasswordResetToken


User = get_user_model()


class AccountService:
    @staticmethod
    def register(username, full_name, email, password, phone, role, address, **extra_fields):
        user = User(username=username, full_name=full_name, email=email, phone=phone, role=role,address=address, **extra_fields)
        user.set_password(password)  
        user.save()
        return user

    @staticmethod
    def login(username: str, password: str):
        user = authenticate(username=username, password=password)
        if not user:
            return None
        refresh = RefreshToken.for_user(user)
        refresh['username'] = user.username
        refresh['role'] = user.role
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def logout(refresh_token: str) -> None:
        token = RefreshToken(refresh_token)
        token.blacklist()
        
    
    @staticmethod
    def change_user_password(user, old_password, new_password):
        if not user.check_password(old_password):
            raise ValidationError({"message": "Mật khẩu cũ không đúng."})
        user.set_password(new_password)
        user.save()
        return "Đổi mật khẩu thành công"
    
    @staticmethod
    def create_token(user):
        expires = timezone.now() + timedelta(hours=1)
        token_obj = PasswordResetToken.objects.create(user=user, expires_at=expires)
        return token_obj

    @staticmethod
    def build_reset_url(request, token_obj):
        path = reverse('password-reset-confirm', args=[str(token_obj.token)])
        return request.build_absolute_uri(path)

    @staticmethod
    def send_reset_email(user, reset_url):
        subject = 'Đặt lại mật khẩu cho PureFlow'
        body = f"Hi {user.full_name or user.username},\n\n"
        body += f"Nhấp vào liên kết bên dưới để đặt lại mật khẩu của bạn (có hiệu lực trong 1 giờ):\n{reset_url}\n\n"
        body += "Nếu bạn không yêu cầu điều này, vui lòng bỏ qua."

        email = EmailMessage(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        email.send(fail_silently=False)
    
    


