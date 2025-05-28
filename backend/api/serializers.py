from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        
    def validate_amount(self, value):
        """
        Validar que el monto sea mayor que cero.
        """
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor que cero.")
        return value
    
    def validate_type(self, value):
        """
        Validar que el tipo de transacción sea válido.
        """
        if value not in dict(Transaction.TRANSACTION_TYPES):
            raise serializers.ValidationError("Tipo de transacción inválido.")
        return value
    
    def validate(self, data):
        """
        Debes verificar que el monto sea superior a un mínimo (por ejemplo, 100).
        """ 
        if data['type'] == 'investment' and data['amount'] < 100:
            raise serializers.ValidationError("Las inversiones deben ser de al menos 100.")
        return data
