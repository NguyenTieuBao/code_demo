from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid
from django.utils import timezone

class User(AbstractUser):
    full_name = models.CharField(max_length=255, null=False)
    
    role = models.CharField(max_length=10, choices=[('Admin', 'admin'), ('Customer', 'Customer')])
    
    phone = models.CharField(max_length=10, unique=True, null=False)
    
    email = models.CharField(max_length=100, null=False)
    
    create_at = models.DateTimeField(auto_now_add=True)
    
    address = models.CharField(max_length=255, null=False)
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'User'
        
class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"ResetToken({self.user.email}, {self.token})"
    
    class Meta:
        db_table = 'PasswordResetToken'
    
    