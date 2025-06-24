from rest_framework import viewsets 
from rest_framework.permissions import IsAuthenticated
from .models import Transaction
from .serializers import TransactionSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TransactionFilter

# api/views.py
from django.core.management import call_command
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(["POST"])
def create_superuser(request):
    print("🔍 Entrando a create_superuser...")

    if User.objects.filter(username="admin").exists():
        print("⚠️ Usuario 'admin' ya existe.")
        return Response({"status": "error", "message": "User already exists"}, status=400)

    try:
        print("🛠 Creando superusuario...")
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        print("✅ Superusuario creado exitosamente.")
        return Response({"status": "success", "message": "Superuser created"}, status=201)
    except Exception as e:
        print(f"❌ Error al crear superusuario: {str(e)}")
        return Response({"status": "error", "message": str(e)}, status=500)

@api_view(["POST"])
def run_migrations(request):
    try:
        call_command('migrate')
        return Response({"status": "success", "message": "Migrations applied"})
    except Exception as e:
        return Response({"status": "error", "message": str(e)})

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all() # Obtener todas las transacciones
    serializer_class = TransactionSerializer # Serializador para la transacción
    permission_classes = [IsAuthenticated] # Solo usuarios autenticados pueden acceder
    filter_backends = [DjangoFilterBackend] # Habilitar el filtrado
    filterset_class = TransactionFilter # Usar el filtro definido en filters.py
    ordering_fields = ['date', 'amount', 'title']  # puedes ordenar por estos campos
    ordering = ['-date']  # orden por defecto: más reciente primero