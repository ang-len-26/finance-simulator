import uuid
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.management import call_command
from django.contrib.auth.models import User
from decimal import Decimal

from backend.api.accounts.models import Account
from backend.api.transactions.models import Transaction

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Endpoint para 'Crear Cuenta'"""
    data = request.data
    
    if User.objects.filter(username=data['username']).exists():
        return Response({'error': 'Usuario ya existe'}, status=400)
    
    try:
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        
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
    """Para 'Probar demo sin registrarse'"""
    demo_user = User.objects.create_user(
        username=f"demo_{uuid.uuid4()}",
        password="demo123"
    )
    
    # Crear cuentas demo
    bcp_account = Account.objects.create(
        user=demo_user,
        name="Cuenta Corriente",
        bank_name="BCP",
        account_type="checking",
        initial_balance=Decimal('5000.00')
    )
    
    savings_account = Account.objects.create(
        user=demo_user,
        name="Cuenta Ahorros",
        bank_name="BBVA",
        account_type="savings", 
        initial_balance=Decimal('10000.00')
    )
    
    cash_account = Account.objects.create(
        user=demo_user,
        name="Efectivo",
        account_type="cash",
        initial_balance=Decimal('500.00')
    )
    
    # Transacciones demo actualizadas
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
        'demo_user': True
    })

@api_view(["POST"])
def create_superuser(request):
    """Endpoint para crear un superusuario"""
    try:
        if User.objects.filter(username="AngelAdminFindTrack").exists():
            return Response({"status": "error", "message": "User already exists"}, status=400)

        User.objects.create_superuser(
            username="AngelAdminFindTrack",
            email="adminfindTrack@findtrack.com",
            password="@FindTrack2025"
        )
        return Response({"status": "success", "message": "Superuser created"}, status=201)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)

@api_view(["POST"])
def run_migrations(request):
    """Endpoint para ejecutar migraciones manualmente"""
    try:
        call_command('migrate')
        return Response({"status": "success", "message": "Migrations applied"})
    except Exception as e:
        return Response({"status": "error", "message": str(e)})
  