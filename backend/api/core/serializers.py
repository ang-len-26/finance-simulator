from rest_framework import serializers
from django.contrib.auth.models import User

from .models import UserProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuarios"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil de usuario"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    account_count = serializers.SerializerMethodField()
    transaction_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'is_demo', 'demo_expires', 'created_at', 
                 'account_count', 'transaction_count')
        read_only_fields = ('is_demo', 'demo_expires', 'created_at')
    
    def get_account_count(self, obj):
        from ..accounts.models import Account
        return Account.objects.filter(user=obj.user).count()
    
    def get_transaction_count(self, obj):
        from ..transactions.models import Transaction
        return Transaction.objects.filter(user=obj.user).count()

class UserLoginSerializer(serializers.Serializer):
    """Serializer para login"""
    username = serializers.CharField()
    password = serializers.CharField()
