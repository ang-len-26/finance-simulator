from rest_framework import viewsets 
from rest_framework.permissions import IsAuthenticated
from .models import Transaction
from .serializers import TransactionSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TransactionFilter

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all() # Obtener todas las transacciones
    serializer_class = TransactionSerializer # Serializador para la transacción
    permission_classes = [IsAuthenticated] # Solo usuarios autenticados pueden acceder
    filter_backends = [DjangoFilterBackend] # Habilitar el filtrado
    filterset_class = TransactionFilter # Usar el filtro definido en filters.py
    ordering_fields = ['date', 'amount', 'title']  # puedes ordenar por estos campos
    ordering = ['-date']  # orden por defecto: más reciente primero