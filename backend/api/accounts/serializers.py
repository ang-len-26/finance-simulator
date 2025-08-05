from rest_framework import serializers
from django.db import models

from backend.api.accounts.models import Account
from backend.api.transactions.models import Transaction

# =====================================================
# SERIALIZERS PARA CUENTAS
# =====================================================
class AccountSerializer(serializers.ModelSerializer):
    current_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    transaction_count = serializers.SerializerMethodField()
    last_transaction_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'bank_name', 'account_number', 'account_type',
            'initial_balance', 'current_balance', 'currency', 'is_active',
            'include_in_reports', 'transaction_count', 'last_transaction_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['current_balance', 'created_at', 'updated_at']
    
    def get_transaction_count(self, obj):
        """Número total de transacciones de esta cuenta"""
        return Transaction.objects.filter(
            models.Q(from_account=obj) | models.Q(to_account=obj)
        ).count()
    
    def get_last_transaction_date(self, obj):
        """Fecha de la última transacción"""
        last_transaction = Transaction.objects.filter(
            models.Q(from_account=obj) | models.Q(to_account=obj)
        ).order_by('-date').first()
        
        return last_transaction.date if last_transaction else None
    
    def validate_name(self, value):
        """Validar que el nombre de cuenta sea único por usuario"""
        user = self.context['request'].user
        
        # Si es actualización, excluir la cuenta actual
        if self.instance:
            existing = Account.objects.filter(
                user=user, name=value
            ).exclude(pk=self.instance.pk)
        else:
            existing = Account.objects.filter(user=user, name=value)
        
        if existing.exists():
            raise serializers.ValidationError("Ya tienes una cuenta con este nombre.")
        return value
    
    def validate_initial_balance(self, value):
        """Validar balance inicial"""
        if value < 0:
            raise serializers.ValidationError("El balance inicial no puede ser negativo.")
        return value

# =====================================================
# SERIALIZERS PARA LISTADOS DE CUENTAS
# =====================================================
class AccountSummarySerializer(serializers.ModelSerializer):
    """Serializer ligero para listados"""
    class Meta:
        model = Account
        fields = ['id', 'name', 'bank_name', 'account_type', 'current_balance', 'currency']
