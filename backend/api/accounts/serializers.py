from rest_framework import serializers

from .models import Account

class AccountSerializer(serializers.ModelSerializer):
    current_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    transaction_count = serializers.SerializerMethodField()
    last_transaction_date = serializers.SerializerMethodField()
    monthly_income = serializers.SerializerMethodField()
    monthly_expenses = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'bank_name', 'account_number', 'account_type',
            'initial_balance', 'current_balance', 'currency', 'is_active',
            'include_in_reports', 'transaction_count', 'last_transaction_date',
            'monthly_income', 'monthly_expenses', 'created_at', 'updated_at'
        ]
        read_only_fields = ['current_balance', 'created_at', 'updated_at']
    
    def get_transaction_count(self, obj):
        """Número total de transacciones de esta cuenta"""
        return obj.transaction_count
    
    def get_last_transaction_date(self, obj):
        """Fecha de la última transacción"""
        return obj.last_transaction_date
    
    def get_monthly_income(self, obj):
        """Ingresos del mes actual"""
        return float(obj.get_monthly_income())
    
    def get_monthly_expenses(self, obj):
        """Gastos del mes actual"""
        return float(obj.get_monthly_expenses())
    
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
    
    def validate_currency(self, value):
        """Validar código de moneda"""
        valid_currencies = ['PEN', 'USD', 'EUR']
        if value.upper() not in valid_currencies:
            raise serializers.ValidationError(f"Moneda debe ser una de: {', '.join(valid_currencies)}")
        return value.upper()

class AccountSummarySerializer(serializers.ModelSerializer):
    """Serializer ligero para listados"""
    class Meta:
        model = Account
        fields = ['id', 'name', 'bank_name', 'account_type', 'current_balance', 'currency', 'is_active']