from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .service import AccountService
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PasswordResetToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone', 'role', 'createdAt', 'status']
        read_only_fields = ['id', 'createAt']

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Username đã tồn tại."
            )
        ],
        error_messages= {
            'blank': 'Username không được để trống.',
            'required': 'Username là bắt buộc.'
        }
    )
    first_name = serializers.CharField(
        error_messages= {
            'blank': 'Họ và tên đệm không được để trống.',
            'required': 'Họ và tên đệm là bắt buộc.'
        }
    )
    last_name = serializers.CharField(
        error_messages= {
            'blank': 'Tên không được để trống.',
            'required': 'Tên là bắt buộc.'
        }
    )
    phone = serializers.CharField(
        max_length=10,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Số điện thoại đã tồn tại."
            )
        ],
        error_messages= {
            'blank': 'Số điện thoại không được để trống.',
            'required': 'Số điện thoại là bắt buộc.',
            'max_length': 'Số điện thoại không được quá 10 số',
        }
    )
    email = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Email đã tồn tại."
            )
        ],
        error_messages= {
            'blank': 'Email không được để trống.',
            'required': 'Email là bắt buộc.'
        }
    )
    password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'},
        min_length=6,
        error_messages= {
            'min_length': 'Mật khẩu phải có ít nhất 6 ký tự.',
            'blank': 'Password không được để trống.',
            'required': 'Password là bắt buộc.'
        })

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password', 'email', 'phone', 'role']
        
    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Số điện thoại chỉ được chứa chữ số.")
        return value
    
    def validate_email(self, value):
        email = value.strip().lower()
        if '@' not in email or '.' not in email.split('@')[1]:
            raise serializers.ValidationError("Email phải có định dạng example@domain.com.")
        return email

    def create(self, validated_data):
        return AccountService.register(**validated_data)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={'blank': 'Username không được để trống.'}
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        error_messages={'black': 'Password không được để trống.'}
    )

    def validate(self, data):
        user = authenticate(
            username=data.get('username'),
            password=data.get('password')
        )
        if not user:
            raise serializers.ValidationError({'detail': "Tài khoản hoặc mật khẩu không chính xác."})
        data['user'] = user
        return data
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'},
        error_messages= {
            'blank': 'Password không được để trống.',
            'required': 'Password là bắt buộc.'
        })
    new_password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'},
        min_length=6,
        error_messages= {
            'min_length': 'Mật khẩu phải có ít nhất 6 ký tự.',
            'blank': 'Password không được để trống.',
            'required': 'Password là bắt buộc.'
        })

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email chưa đăng ký")
        return value

class PasswordResetSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        try:
            token_obj = PasswordResetToken.objects.get(token=attrs['token'])
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Token không hợp lệ")
        if token_obj.is_expired():
            raise serializers.ValidationError("Token đã hết hạn")
        attrs['token_obj'] = token_obj
        return attrs

    def save(self):
        token_obj = self.validated_data['token_obj']
        user = token_obj.user
        user.set_password(self.validated_data['new_password'])
        user.save()
        token_obj.delete()
        return user

    
