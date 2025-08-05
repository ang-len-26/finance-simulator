from rest_framework import serializers

from .models import Category, Transaction

# =====================================================
# SERIALIZERS PARA TRANSACCIONES
# =====================================================
class TransactionSerializer(serializers.ModelSerializer):
    from_account_name = serializers.CharField(source='from_account.name', read_only=True)
    to_account_name = serializers.CharField(source='to_account.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)  # NUEVO
    category_icon = serializers.CharField(source='category.icon', read_only=True)  # NUEVO
    category_color = serializers.CharField(source='category.color', read_only=True)  # NUEVO
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'title', 'amount', 'type', 'date', 'description',
            'from_account', 'to_account', 'from_account_name', 'to_account_name',
            'category', 'category_name', 'category_icon', 'category_color',  # NUEVO
            'reference_number', 'location', 'tags', 'is_recurring', 
            'recurring_frequency', 'parent_transaction', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_amount(self, value):
        """Validar monto"""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor que cero.")
        return value
    
    def validate_type(self, value):
        """Validar tipo de transacción"""
        if value not in dict(Transaction.TRANSACTION_TYPES):
            raise serializers.ValidationError("Tipo de transacción inválido.")
        return value
    
    def validate_from_account(self, value):
        """Validar que la cuenta pertenezca al usuario"""
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("La cuenta de origen no te pertenece.")
        return value
    
    def validate_to_account(self, value):
        """Validar cuenta destino si existe"""
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("La cuenta destino no te pertenece.")
        return value
    
    def validate_category(self, value):
        """Validar que la categoría sea apropiada para el tipo de transacción"""
        if value:
            # Verificar que la categoría esté activa
            if not value.is_active:
                raise serializers.ValidationError("Esta categoría no está disponible.")
        return value
    
    def validate(self, data):
        """Validaciones complejas"""
        transaction_type = data.get('type')
        from_account = data.get('from_account')
        to_account = data.get('to_account')
        amount = data.get('amount', 0)
        category = data.get('category')
        
        # Validar compatibilidad categoría-tipo
        if category:
            if transaction_type == 'income' and category.category_type == 'expense':
                raise serializers.ValidationError("No puedes asignar una categoría de gasto a un ingreso.")
            elif transaction_type == 'expense' and category.category_type == 'income':
                raise serializers.ValidationError("No puedes asignar una categoría de ingreso a un gasto.")
        
        # Validaciones por tipo de transacción (las mismas de antes)
        if transaction_type == 'transfer':
            if not to_account:
                raise serializers.ValidationError("Las transferencias requieren cuenta destino.")
            if from_account == to_account:
                raise serializers.ValidationError("No puedes transferir a la misma cuenta.")
        
        elif transaction_type == 'income':
            if not to_account:
                raise serializers.ValidationError("Los ingresos requieren cuenta destino.")
        
        elif transaction_type in ['expense', 'investment', 'loan', 'debt', 'savings']:
            if not from_account:
                raise serializers.ValidationError(f"{transaction_type.title()} requiere cuenta de origen.")
        
        # Validaciones de negocio (las mismas de antes)
        if transaction_type == 'investment' and amount < 100:
            raise serializers.ValidationError("Las inversiones deben ser de al menos $100.")
        
        if transaction_type == 'loan' and amount > 10000:
            raise serializers.ValidationError("Los préstamos no pueden exceder $10,000.")
        
        if transaction_type == 'expense' and amount > 5000:
            raise serializers.ValidationError("Los gastos no pueden exceder $5,000.")
        
        return data

# =====================================================
# SERIALIZERS PARA LISTADOS Y REPORTES DE TRANSACCIONES
# =====================================================
class TransactionSummarySerializer(serializers.ModelSerializer):
    """Serializer ligero para listados y reportes"""
    from_account_name = serializers.CharField(source='from_account.name', read_only=True)
    to_account_name = serializers.CharField(source='to_account.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)  # NUEVO
    category_icon = serializers.CharField(source='category.icon', read_only=True)  # NUEVO
    category_color = serializers.CharField(source='category.color', read_only=True)  # NUEVO
    is_positive = serializers.SerializerMethodField()  # NUEVO
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'title', 'amount', 'type', 'date', 
            'from_account_name', 'to_account_name',
            'category_name', 'category_icon', 'category_color', 'is_positive'  # NUEVO
        ]
    
    def get_is_positive(self, obj):
        """Determinar si es ingreso (positivo) o gasto (negativo)"""
        return obj.type == 'income'
       
# =====================================================
# SERIALIZERS PARA ANÁLISIS FINANCIERO
# =====================================================
class CategorySerializer(serializers.ModelSerializer):
    transaction_count = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'icon', 'color', 'category_type',
            'parent', 'parent_name', 'is_active', 'sort_order',
            'transaction_count', 'subcategories', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_transaction_count(self, obj):
        """Número de transacciones en esta categoría"""
        user = self.context.get('request').user if self.context.get('request') else None
        if user:
            return Transaction.objects.filter(category=obj, user=user).count()
        return 0
    
    def get_subcategories(self, obj):
        """Subcategorías anidadas"""
        if obj.subcategories.exists():
            return CategorySummarySerializer(
                obj.subcategories.filter(is_active=True), 
                many=True, 
                context=self.context
            ).data
        return []
    
    def validate_color(self, value):
        """Validar formato hexadecimal"""
        if not value.startswith('#') or len(value) != 7:
            raise serializers.ValidationError("Color debe estar en formato hexadecimal (#ffffff)")
        return value

# =====================================================
# SERIALIZERS PARA REPORTES FINANCIEROS
# =====================================================    
class CategorySummarySerializer(serializers.ModelSerializer):
    """Serializer ligero para categorías"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'color', 'category_type']

