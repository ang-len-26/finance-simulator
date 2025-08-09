import os
import uuid
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.management import call_command
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from ..accounts.models import Account
from ..transactions.models import Transaction
from .models import UserProfile
from .serializers import UserRegistrationSerializer, UserProfileSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Endpoint para 'Crear Cuenta' con serializer"""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=400)
    
    try:
        user = serializer.save()
        
        # Crear perfil de usuario
        UserProfile.objects.create(user=user)
        
        # Crear cuenta por defecto (Efectivo)
        Account.objects.create(
            user=user,
            name="Efectivo",
            account_type="cash",
            initial_balance=Decimal('0.00')
        )
        
        return Response({
            'message': 'Usuario creado exitosamente',
            'user_id': user.id
        }, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_demo_user(request):
    """Para 'Probar demo sin registrarse' - Con variables de entorno SEGURAS"""
    
    demo_prefix = os.getenv('DEMO_USER_PREFIX', 'demo_user')
    demo_password = os.getenv('DEMO_PASSWORD', 'demo123')
    demo_duration = int(os.getenv('DEMO_DURATION_HOURS', '24'))
    
    # Balances desde variables de entorno
    bcp_balance = Decimal(os.getenv('DEMO_BCP_BALANCE', '5000.00'))
    bbva_balance = Decimal(os.getenv('DEMO_BBVA_BALANCE', '10000.00'))
    cash_balance = Decimal(os.getenv('DEMO_CASH_BALANCE', '500.00'))
    
    demo_user = User.objects.create_user(
        username=f"{demo_prefix}_{uuid.uuid4()}",
        password=demo_password
    )
    
    # Crear perfil demo con expiración
    UserProfile.objects.create(
        user=demo_user,
        is_demo=True,
        demo_expires=timezone.now() + timedelta(hours=demo_duration)
    )
    
    # Crear cuentas demo con balances desde .env
    bcp_account = Account.objects.create(
        user=demo_user,
        name="Cuenta Corriente",
        bank_name="BCP",
        account_type="checking",
        initial_balance=bcp_balance
    )
    
    savings_account = Account.objects.create(
        user=demo_user,
        name="Cuenta Ahorros",
        bank_name="BBVA",
        account_type="savings", 
        initial_balance=bbva_balance
    )
    
    cash_account = Account.objects.create(
        user=demo_user,
        name="Efectivo",
        account_type="cash",
        initial_balance=cash_balance
    )
    
    # Transacciones demo (mantener las existentes)
    sample_transactions = [
        {'title': 'Sueldo', 'amount': 3000, 'type': 'income', 'date': '2024-08-01', 'to_account': bcp_account},
        {'title': 'Supermercado', 'amount': 150, 'type': 'expense', 'date': '2024-08-02', 'from_account': bcp_account},
        {'title': 'Netflix', 'amount': 15.99, 'type': 'expense', 'date': '2024-08-03', 'from_account': bcp_account},
        {'title': 'Transferencia a Ahorros', 'amount': 500, 'type': 'transfer', 'date': '2024-08-04', 'from_account': bcp_account, 'to_account': savings_account},
        {'title': 'Retiro ATM', 'amount': 200, 'type': 'transfer', 'date': '2024-08-05', 'from_account': bcp_account, 'to_account': cash_account},
        {'title': 'Inversión', 'amount': 1000, 'type': 'investment', 'date': '2024-08-06', 'from_account': savings_account},
        {'title': 'Pago servicios', 'amount': 100, 'type': 'expense', 'date': '2024-08-07', 'from_account': bcp_account},
        {'title': 'Freelance', 'amount': 800, 'type': 'income', 'date': '2024-08-08', 'to_account': bcp_account},
        {'title': 'Restaurante', 'amount': 60, 'type': 'expense', 'date': '2024-08-09', 'from_account': cash_account},
        {'title': 'Gasolina', 'amount': 35, 'type': 'expense', 'date': '2024-08-10', 'from_account': bcp_account},
    ]
    
    for trans_data in sample_transactions:
        Transaction.objects.create(**trans_data, user=demo_user)
    
    # Actualizar balances
    bcp_account.update_balance()
    savings_account.update_balance()
    cash_account.update_balance()
    
    # Retornar tokens para acceso inmediato
    refresh = RefreshToken.for_user(demo_user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'demo_user': True,
        'expires_at': UserProfile.objects.get(user=demo_user).demo_expires
    })

@api_view(["POST"])
def create_superuser(request):
    
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_password = os.getenv('ADMIN_PASSWORD')
    
    # Validar que las variables estén configuradas
    if not all([admin_username, admin_email, admin_password]):
        return Response({
            "status": "error", 
            "message": "Variables de entorno requeridas: ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD"
        }, status=500)
    
    try:
        if User.objects.filter(username=admin_username).exists():
            return Response({
                "status": "error", 
                "message": f"Admin user '{admin_username}' already exists"
            }, status=400)

        user = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password
        )
        
        # Crear perfil para el admin
        UserProfile.objects.create(user=user)
        
        return Response({
            "status": "success", 
            "message": f"Superuser '{admin_username}' created successfully"
        }, status=201)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)

@api_view(["POST"])
def run_migrations(request):
    """Endpoint para ejecutar migraciones manualmente"""
    try:
        call_command('migrate')
        return Response({"status": "success", "message": "Migrations applied successfully"})
    except Exception as e:
        return Response({"status": "error", "message": str(e)})

@api_view(['GET'])
def user_profile(request):
    """Endpoint para obtener perfil del usuario autenticado"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        # Crear perfil si no existe
        profile = UserProfile.objects.create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
