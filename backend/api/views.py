from rest_framework import viewsets 
from rest_framework.permissions import IsAuthenticated
from .models import Transaction
from .serializers import TransactionSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TransactionFilter
from rest_framework.permissions import AllowAny

# api/views.py
from django.core.management import call_command
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['POST'])
@permission_classes([AllowAny])  # type: ignore # 👈 Esto hace la vista accesible sin login
def run_migrations(request):
    call_command('migrate')
    return Response({"status": "migraciones aplicadas correctamente"})


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all() # Obtener todas las transacciones
    serializer_class = TransactionSerializer # Serializador para la transacción
    permission_classes = [IsAuthenticated] # Solo usuarios autenticados pueden acceder
    filter_backends = [DjangoFilterBackend] # Habilitar el filtrado
    filterset_class = TransactionFilter # Usar el filtro definido en filters.py
    ordering_fields = ['date', 'amount', 'title']  # puedes ordenar por estos campos
    ordering = ['-date']  # orden por defecto: más reciente primero